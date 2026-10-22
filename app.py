# A Locus ID is NEVER sent directly to UniProt/InterPro as if it were a protein accession.
def normalize_locus(locus, organism):
    """Return (clean_locus, error, note). Validates the format for the chosen organism."""
    locus = re.sub(r"\s+", "", locus or "")
    if not locus:
        return "", "Locus ID is empty. Enter a Locus ID, for example At1g01010.", None
    if not organism:
        return locus, "Organism is empty. Enter the scientific name of the organism (e.g. Oryza sativa).", None

    if organism == ARABIDOPSIS:
        note = None
        # "AT1G01010.1" is a transcript/protein model; the locus is the part before the dot
        if re.match(r"^AT[1-5CM]G\d{5}\.\d+$", locus, re.IGNORECASE):
            locus, note = locus.split(".")[0], "Isoform suffix removed: a Locus ID identifies the gene, not a single transcript."
        locus = locus.upper()
        if not ARABIDOPSIS_LOCUS_RE.match(locus):
            return locus, (
                f"'{locus}' is not a valid Arabidopsis thaliana Locus ID. "
                "Expected the form AT#G##### (for example At1g01010), where # after AT is 1-5, C or M."
            ), None
        return locus, None, note

    if not GENERIC_LOCUS_RE.match(locus):
        return locus, (
            f"'{locus}' does not look like a valid Locus ID. Use only letters, digits and _ . - : "
            "(2-64 characters)."
        ), None
    return locus, None, None


def ncbi_get(url, params, email, api_key):
    """GET an NCBI E-utilities endpoint and return parsed JSON (email / API key are optional)."""
    full = {"tool": TOOL_NAME, "retmode": "json", **params}
    if email:
        full["email"] = email
    if api_key:
        full["api_key"] = api_key
    # NCBI allows ~3 requests/s without an API key and ~10/s with one
    time.sleep(0.12 if api_key else 0.35)
    r = requests.get(url, params=full, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def resolve_ncbi_gene(locus, organism, email, api_key):
    """Locus ID + organism -> NCBI Gene record. Returns a dict with the chosen gene and all candidates."""
    org = organism.replace('"', "")
    term = f'"{locus}"[All Fields] AND "{org}"[Organism] AND alive[prop]'
    found = ncbi_get(NCBI_ESEARCH, {"db": "gene", "term": term, "retmax": 20}, email, api_key)
    ids = found.get("esearchresult", {}).get("idlist", [])
    if not ids:
        raise LookupFailed(
            f"No NCBI Gene record found for Locus ID '{locus}' in {organism}. "
            "Check the spelling and that the selected organism is correct."
        )

    summary = ncbi_get(NCBI_ESUMMARY, {"db": "gene", "id": ",".join(ids)}, email, api_key).get("result", {})
    docs = [summary[uid] for uid in summary.get("uids", []) if uid in summary]
    if not docs:
        raise LookupFailed(f"NCBI found gene IDs {', '.join(ids)} but returned no summary for them.")

    # Prefer records that literally mention the locus (name, alias, locus tag ...)
    exact = [d for d in docs if locus.lower() in json.dumps(d).lower()]
    pool = exact or docs
    return {
        "gene_id": str(pool[0]["uid"]),
        "summary": pool[0],
        "candidates": [
            {"gene_id": str(d["uid"]), "name": d.get("name"), "description": d.get("description")} for d in pool
        ],
    }


def resolve_ncbi_proteins(gene_id, email, api_key):
    """NCBI Gene ID -> linked protein records (RefSeq first, NP_ before XP_)."""
    prot_ids = []
    for linkname in ("gene_protein_refseq", "gene_protein"):  # fall back to all linked proteins
        data = ncbi_get(NCBI_ELINK, {"dbfrom": "gene", "db": "protein", "id": gene_id, "linkname": linkname},
                        email, api_key)
        for linkset in data.get("linksets", []):
            for db in linkset.get("linksetdbs", []):
                prot_ids += [str(x) for x in db.get("links", [])]
        if prot_ids:
            break
    if not prot_ids:
        raise LookupFailed(
            f"NCBI Gene {gene_id} has no linked protein record (it may be a non-coding gene or pseudogene)."
        )

    summary = ncbi_get(NCBI_ESUMMARY, {"db": "protein", "id": ",".join(prot_ids[:20])}, email, api_key).get("result", {})
    proteins = [
        {"uid": uid, "accession": summary[uid].get("accessionversion") or summary[uid].get("caption"),
         "title": summary[uid].get("title")}
        for uid in summary.get("uids", []) if uid in summary
    ]
    proteins = [p for p in proteins if p["accession"]]
    if not proteins:
        raise LookupFailed(f"NCBI Gene {gene_id} links to protein records, but no accessions could be read.")
    proteins.sort(key=lambda p: (not p["accession"].startswith("NP_"), p["accession"]))
    return proteins


def uniprot_search(query):
    """Search UniProtKB; return matching entries with reviewed (Swiss-Prot) entries first."""
    r = requests.get(
        UNIPROTKB_SEARCH,
        params={"query": query, "format": "json", "size": 25,
                "fields": "accession,reviewed,protein_name,gene_names,organism_name"},
        headers={"Accept": "application/json"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    results = r.json().get("results", [])
    return sorted(results, key=lambda e: (not e.get("entryType", "").startswith("UniProtKB reviewed"),
                                          e.get("primaryAccession", "")))


def find_uniprot_for_locus(locus, organism, gene_id):
    """Find UniProtKB entries for a locus. Returns (accessions, method_description)."""
    org = organism.replace('"', "")
    org_filter = f"organism_id:{ARABIDOPSIS_TAXID}" if organism == ARABIDOPSIS else f'organism_name:"{org}"'
    strategies = []
    if gene_id:  # most reliable: UniProt cross-references NCBI GeneID
        strategies.append((f"NCBI GeneID cross-reference ({gene_id})", f"xref:geneid-{gene_id}"))
    strategies.append((f"gene name / ordered locus name '{locus}' in {organism}",
                       f'(gene:"{locus}") AND ({org_filter})'))
    for label, query in strategies:
        results = uniprot_search(query)
        if results:
            return [e["primaryAccession"] for e in results], label
    raise LookupFailed(
        f"No UniProt entry found for Locus ID '{locus}' in {organism}. "
        "The gene may have no UniProt record, or the organism selection may be wrong."
    )


def resolve_locus_to_uniprot(locus, organism, email, api_key):
    """Locus ID -> UniProt accession (via NCBI Gene when possible). Shows what was resolved."""
    gene = None
    try:
        gene = resolve_ncbi_gene(locus, organism, email, api_key)
        warn_if_ambiguous_gene(gene)
    except LookupFailed as e:
        st.info(f"{e} Trying UniProt directly with the gene name instead.")

    accessions, method = find_uniprot_for_locus(locus, organism, gene["gene_id"] if gene else None)
    accession = accessions[0]
    show_locus_identifiers(locus, organism, gene=gene, uniprot=accession)
    st.caption(f"UniProt entry found via {method}.")
    if len(accessions) > 1:
        st.warning("Multiple UniProt entries match this Locus ID; using the first "
                   f"(reviewed entries are ranked first). Others: {', '.join(accessions[1:])}")
    return accession


def warn_if_ambiguous_gene(gene):
    if len(gene["candidates"]) > 1:
        others = "; ".join(f"{c['gene_id']} ({c['name']}: {c['description']})" for c in gene["candidates"][1:])
        st.warning(f"Multiple NCBI Gene records match this Locus ID. Using the first (Gene ID {gene['gene_id']}). "
                   f"Other matches: {others}")
