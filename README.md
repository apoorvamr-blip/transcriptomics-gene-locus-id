# bio-api-tester

A minimal Streamlit app that queries three biological APIs live, starting from either a **FASTA protein sequence** or a **Locus ID**:

- **NCBI** (BLAST URL API and E-utilities: esearch / esummary / elink)
- **UniProt** REST API (UniParc sequence lookup, UniProtKB search and record)
- **InterPro** API

The returned JSON is displayed directly in the app.

All data is fetched live from the APIs. No local biological data (CSV, Excel, JSON, FASTA, etc.) is used, and neither sequences nor Locus IDs are written to disk. No API keys are stored in the code.

## Install

```bash
pip install -r requirements.txt
```

`requirements.txt` only needs `streamlit` and `requests`.

## Run

```bash
streamlit run app.py
```

## Input type

Choose the input method with the **Input type** selector at the top of the app:

1. **FASTA Protein Sequence**
2. **Locus ID**

### 1. FASTA Protein Sequence

Paste either:

- a full FASTA record, e.g.

  ```
  >my_protein
  MKTIIALSYIFCLVFADYKDDDDK
  ```

- or just the amino-acid sequence, with no header.

The app removes whitespace and line breaks, drops the header (if any), upper-cases the sequence and checks that it contains only valid amino-acid letters. If several FASTA records are pasted, only the first is used. The parsed sequence length is shown before you query. Use **Load example FASTA** to fill in human hemoglobin subunit alpha.

| Button | Workflow |
| --- | --- |
| **Query UniProt** | Computes the sequence's MD5 checksum and searches UniParc (UniProt's sequence archive) for an exact match, picks the matching UniProtKB accession (reviewed Swiss-Prot entries first), then fetches that record from UniProtKB. |
| **Query InterPro** | Finds the UniProt accession the same way, then queries InterPro with that accession. |
| **Query NCBI** | Runs `blastp` against NCBI's `nr` database through the BLAST URL API, takes the top-hit accession, then looks it up in the protein database with esearch. |

Notes:

- UniProt and InterPro lookups need an **exact** sequence match. Variants, fragments or novel sequences give a "no match" message.
- NCBI BLAST is asynchronous and can take from several seconds to a few minutes. To speed it up, change `BLAST_DB` at the top of `app.py` (for example to `swissprot` or `refseq_protein`).
- If the same sequence exists in several UniProt entries, the first one is used and the others are listed.

### 2. Locus ID

Enter a **Locus ID** (for example `At1g01010`) and choose the **Organism**. Locus IDs are organism-specific gene identifiers, **not** universal protein accessions, so the app never puts a Locus ID straight into a UniProt or InterPro protein URL. It resolves the ID first:

```
Locus ID + organism
   -> NCBI Gene record (esearch + esummary, db=gene)
   -> NCBI protein accession(s) (elink gene -> protein, RefSeq NP_ accessions first)
   -> UniProt accession (UniProtKB search by NCBI GeneID cross-reference,
                         falling back to a gene-name search restricted to the organism)
   -> InterPro (queried with the resolved UniProt accession)
```

| Button | Workflow |
| --- | --- |
| **Query NCBI** | Resolves the Gene record and its linked protein accession(s), shows them, then looks the primary protein accession up in the NCBI protein database. Gene summary, linked proteins and esearch JSON are shown. |
| **Query UniProt** | Resolves the Gene ID, finds the UniProtKB entry (reviewed entries first), shows the resolved UniProt accession, then fetches and displays the UniProtKB JSON record. |
| **Query InterPro** | Resolves the UniProt accession the same way, then queries InterPro with it. |

Organism handling:

- **Arabidopsis thaliana** is the default (NCBI Taxonomy ID 3702). IDs must look like `AT1G01010` (case-insensitive). A transcript suffix such as `.1` is removed automatically.
- **Other / custom organism**: type the scientific name (e.g. `Oryza sativa`). The Locus ID is then checked only for a generic format, and the name is used to restrict the NCBI and UniProt searches.
- The same Locus ID can mean different genes in different organisms, so always select the right organism.

Resolved identifiers (Locus ID, NCBI Gene ID, NCBI protein accession(s), UniProt accession) are displayed above the JSON.

Messages are shown (the app does not crash) for: empty or invalid Locus ID, no matching NCBI record, no linked protein, no matching UniProt record, no InterPro record, multiple/ambiguous matches (the first, best-ranked match is used and the others are listed), request timeouts and other request failures.

## NCBI email and API key

Both are optional; enter your own in the app. In FASTA mode the email is sent to BLAST and E-utilities and the API key to E-utilities. In Locus ID mode both are sent to every E-utilities call. An API key raises NCBI's rate limit from about 3 to 10 requests per second. Nothing is stored.

## Examples

- **FASTA:** click **Load example FASTA** (human hemoglobin subunit alpha, UniProt `P69905`) and press any query button.
- **Locus ID:** select **Locus ID**, keep **Arabidopsis thaliana**, enter `At1g01010` and press any query button.
