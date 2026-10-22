# TP53 ChIP-seq and RNA-seq Analysis Dashboard

An interactive bioinformatics application built using **Python and Streamlit** to explore protein information, TP53 ChIP-seq binding patterns, and RNA-seq gene expression data.

## Project Overview

This project integrates a protein information lookup tool with an exploratory analysis dashboard for TP53 ChIP-seq and RNA-seq data. The application allows users to upload datasets, examine gene expression patterns, identify potential TP53 binding regions, and explore relationships between binding and gene expression.

## Features

### 1. Protein Identification and Annotation
- Search using a protein FASTA sequence or gene/protein Locus ID.
- Retrieve information from NCBI BLAST, Gene, and Protein databases.
- Access UniProt and UniParc records.
- Explore protein domain and family information through InterPro.

### 2. TP53 ChIP-seq Analysis
- Upload ChIP-seq peak files in BED format.
- Annotate genomic peaks to nearby genes using transcription start sites (TSS).
- Explore potential relationships between TP53 binding regions and gene expression.
- Filter and inspect motif-hit results when FIMO output is available.

### 3. RNA-seq Analysis
- Upload an RNA-seq count matrix.
- Normalize counts using counts per million (CPM).
- Apply log2(CPM + 1) transformation.
- Visualize sample relationships using principal component analysis (PCA).
- Compare expression patterns between selected samples.

### 4. Integrated Analysis
- Combine peak annotations with gene expression measurements.
- Explore differences in expression between genes with and without nearby TP53 binding peaks.
- Perform an exploratory Mann–Whitney U test.
- Optionally perform pathway enrichment analysis using GSEApy and Enrichr.
- Export analysis tables as CSV or TSV files.

## Repository Structure

```text
TP53-ChIPseq-RNAseq-analysis-/
│
├── app.py                  # Streamlit application
├── requirements.txt         # Python dependencies
├── environment.yml          # Conda environment configuration
├── tp53_analysis.ipynb      # Original analysis notebook
│
├── data/                    # Input datasets
├── results/                 # Analysis results
├── images/                  # Figures and visualizations
│
└── README.md                # Project documentation
```

*The exact files and folders may vary depending on the version of the repository.*

## Installation

### Prerequisites
- Python 3.10 or a compatible Python version.
- Git.
- Internet access for external database lookups and optional pathway enrichment.

### Step 1: Clone the repository

```bash
git clone https://github.com/Angell-codes/TP53-ChIPseq-RNAseq-analysis-.git
cd TP53-ChIPseq-RNAseq-analysis-
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

Activate the environment.

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

If you prefer Conda and the repository's environment file is compatible with your setup, you can use:

```bash
conda env create -f environment.yml
conda activate <environment-name>
```

Replace `<environment-name>` with the environment name specified in `environment.yml`.

## Running the Application

Start the Streamlit dashboard using:

```bash
streamlit run app.py
```

The application will display a local URL in the terminal, usually:

```text
http://localhost:8501
```

Open the URL in your browser to access the dashboard.

## Input Data Formats

### RNA-seq Count Matrix

Upload a CSV or TSV file containing gene identifiers and sample-level raw counts.

Example:

| Gene_ID | Control_1 | Treatment_1 |
|---|---:|---:|
| ENSG00000141510 | 120 | 185 |
| ENSG00000171862 | 45 | 32 |
| ENSG00000123415 | 210 | 275 |

The application expects gene identifiers and numeric sample-count columns. Confirm that the uploaded file's structure matches the application's input requirements.

### ChIP-seq Peak File

Upload a BED-format file containing genomic peak coordinates.

Typical columns include:

```text
chromosome    start    end
chr17         7660000  7660500
chr17         7670000  7670600
```

The genomic coordinates should use the same reference genome as the annotation file.

### Gene Annotation File

A GTF annotation file is used to identify genes and transcription start sites. Ensure that the annotation corresponds to the reference genome used for the ChIP-seq peaks.

### Optional Motif Results

FIMO output can be uploaded to inspect and filter predicted motif hits. A scanned-region BED file can also be supplied where required by the application.

## Analysis Workflow

1. Launch the Streamlit application.
2. Select the **Protein Identification & Annotation** tab to query protein information, or open the **TP53 ChIP-seq & RNA-seq** tab for genomic analysis.
3. Upload the required RNA-seq count matrix, ChIP-seq BED file, and gene annotation file.
4. Select the relevant samples and analysis settings.
5. Explore expression summaries, PCA plots, peak annotations, and integrated results.
6. Review the statistical outputs alongside the stated limitations.
7. Download the generated result tables for further analysis.

## Scientific Considerations and Limitations

- **Exploratory RNA-seq analysis:** CPM normalization and log transformation are useful for visualization but do not replace a complete differential expression workflow.
- **Limited replication:** If each condition contains only one sample, reliable biological variability estimates and formal differential expression conclusions cannot be established.
- **Independent experiments:** ChIP-seq and RNA-seq datasets generated in different experiments may not represent directly matched biological conditions.
- **Peak-to-gene assignment:** Assigning a peak to a nearby gene based on its distance from the TSS does not prove that the peak regulates that gene.
- **Motif analysis:** Uploaded FIMO results represent the supplied motif-scan output. The dashboard does not itself execute a new FIMO scan.
- **Statistical interpretation:** Exploratory group comparisons should not be interpreted as definitive evidence of TP53-mediated regulation.
- **Pathway enrichment:** Enrichment results depend on the selected gene list, background set, annotation database, and statistical settings.
- **Signal-level analysis:** The dashboard does not directly calculate ChIP-seq signal from BigWig files.

Interpret the results as exploratory evidence that can guide further validation, rather than as definitive proof of a regulatory mechanism.

## Technologies Used

- Python
- Streamlit
- Pandas and NumPy
- Matplotlib
- scikit-learn
- SciPy
- Requests
- GSEApy (optional pathway enrichment)

## Future Improvements

- Add automated retrieval of the repository's datasets.
- Integrate direct BigWig signal visualization.
- Implement de novo execution of motif scanning and matched-background enrichment.
- Support statistically appropriate differential expression analysis when sufficient biological replicates are available.
- Add more interactive genomic visualizations and downloadable reports.

## Acknowledgements

This project builds on the TP53 ChIP-seq and RNA-seq analysis resources available in the project repository and integrates them with an interactive Streamlit interface for exploratory bioinformatics analysis.

## License

Refer to the repository's license file for the applicable terms of use.
