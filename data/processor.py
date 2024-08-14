import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join('..')))
from src import *
import fitz
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCRIPT_DIR = os.getcwd()
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FOLDER_PATH = os.path.join(PARENT_DIR, 'data')
PDF_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, 'pdf')
CSV_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH, 'csv')

os.makedirs(CSV_FOLDER_PATH, exist_ok=True)

po2015_1885W = {
    'id': '1885W', 
    'title': 'A Multi-Ethnic Genotyping Array for the Next Generation of Association Studies.', 
    'authors': '''C. R. Gignoux, G. L. Wojcik1, H. R. Johnston2, C. Fuchsberger3, S. Shringarpure1, 
                A. R. Martin1, S. Rosse4, N. Zubair4, D. Taliun3, R. Welch3, C. Pethigoya5, J. O’Connell5, L. McAuliffe5, 
                C. Rosenow5, N. S. Abdul-husn6, G. Belbin6, H. M. Kang3, G. Abecasis3, M. Boehnke3, Z. S. Qin2, J. M. Romm7, 
                C. A. Haiman8, C. Kooperberg4, R. J. Loos6, T. C. Matise9, K. E. North10, C. Carlson4, K. C. Barnes11, 
                C. D. Bustamante1, E. E. Kenny6, Population Architecture using Genomics and Epidemiology (PAGE) Study. 1) 
                Department of Genetics, Stanford University School of Medicine, Stanford, CA; 2) Department of Biostatistics 
                and Bioinformatics, Rollins School of Public Health, Atlanta, GA; 3) Department of Biostatistics, School of 
                Public Health, University of Michigan, Ann Arbor, MI; 4) Fred Hutchinson Cancer Research Center, Seattle, WA; 
                5) Illumina Inc. , San Diego, CA; 6) Department of Genetic and Genomic Sciences, Icahn School of Medicine at 
                Mount Sinai, New York, NY; 7) Center for Inherited Disease Research, Johns Hopkins University, Baltimore, MD; 
                8) Department of Preventive Medicine, Norris Comprehensive Cancer Center, Keck School of Medicine, University 
                of Southern California, Los Angeles, CA; 9) Department of Genetics, Rutgers University, Piscataway, NJ; 10) 
                Department of Epidemiology, School of Public Health, University of North Carolina at Chapel Hill, Chapel Hill, 
                NC; 11) Department of Medicine, Johns Hopkins University School of Medicine, Baltimore, MD.''',
    'content': '''In the past decade, genome-wide association studies (GWAS) have been extraordinarily successful 
                in uncovering genetic factors underlying complex traits. However much of this work has only been performed in 
                populations of European descent. To address this disparity, a collaboration between Illumina, PAGE, CAAPA 
                (Consortium on Asthma among African-ancestry Populations in the Americas), and T2D Genes Consortium developed 
                the 1. 9M SNP Multi-Ethnic Genotyping Array (MEGA). This array is designed to be a single platform to interrogate 
                diverse variation from across the frequency spectrum and screen for prior genetic discoveries. The GWAS backbone 
                is informed by whole genome sequences from the 1000 Genomes Project (TGP) and CAAPA, with additional compatibility 
                from the Illumina HumanCore array. We developed a novel cross-population tag SNP strategy to maximize imputation 
                accuracy for low frequency variants across six continental populations, with improved performance from previous 
                generations of arrays. Importantly the performance of the array is high across all continental TGP superpopulations 
                (>90% accuracy for MAF >=1%). We chose rare, functional candidates from >36,000 multi-ethnic exomes, prioritizing 
                loss-of-function and predicted damaging sites. We also curated variants with domain experts, including boosting 
                coverage in regions of interest (e. g. MHC), over 5,000 ancestry informative markers, uniparental markers, and over 
                25,000 variants of clinical, prior GWAS, pharmacogenetic, and eQTL importance. A reference panel of several thousand 
                individuals, including HGDP and a large panel of Native Americans, is available on MEGA to aid in rare variant calling, 
                ancestry characterization, and admixture analyses. We will present data on MEGA genotyping of >60,000 African-American, 
                Hispanic/Latino, East Asian and Native Hawaiian individuals from PAGE and CAAPA. We will describe imputation performance 
                in these populations and others, including the improvements to imputation accuracy derived from larger whole genome 
                reference panels. Further details, summary statistics and other relevant information generated from the platform will be 
                placed in a centralized community repository at www. pagestudy. org/mega. We intend MEGA to be a platform and an analytical 
                resource for researchers interested in large-scale studies of diverse populations from across the globe.''',
    'header': 'Bioinformatics and Genomic Technology',
    'year': int(2015)
}

po2015_1885W['content'] = re.sub(r'\s*\n\s*', ' ', po2015_1885W['content'])
po2015_1885W['authors'] = re.sub(r'\s*\n\s*', ' ', po2015_1885W['authors'])

po2015_3108T = {
    'id': '3108T', 
    'title': '3D-NOME: an integrated 3-Dimensional NucleOme Modeling Engine for data-driven simulation of spatial genome organization.', 
    'authors': '''D. Plewczynski1,2,3, P. Szalaj3,4, Z. Tang2, P. Michalski2, M. Pi tal1, O. Luo2, X. Li2, Y. Ruan2. 1) Centre of New Technologies, 
                University of Warsaw, 00-927 Warsaw, Poland; 2) The Jackson Laboratory for Genomic Medicine, Farmington, CT, USA; 3) Centre for Innovative 
                Research, Medical University of Bialystok, Bialystok, Poland; 4) I-BioStat, Hasselt University, Belgium.''',
    'content': '''Background: Chromosomal folding are important features of genome organization, which play critical roles in genome functions, including 
                transcriptional regulation. Using 3C-based mapping technologies to render long-range chromatin interactions has started to reveal some basic 
                principles of spatial genome organization. Among 3D genome mapping technologies, ChIA-PET is unique in its ability to generate multiple datasets 
                (in a single experiment), including binding sites, enriched chromatin interactions (mediated by specific protein factors), as well as non-enriched 
                interactions that reflect topological neighborhoods of higher-order associations. The multifarious nature of ChIA-PET data represents an important 
                advantage in capturing multi-layer structural-functional information, but also imposes new challenges in multi-scale modeling of 3D genome. Results: 
                We report the development of 3D-NOME (3-Dimensional NucleOme Modeling Engine), for processing ChIA-PET data, which includes four components: 1) 
                identifying interactions from ChIAPET reads, 2) multidimensional scaling on proximity graph distances for rapid low-resolution structural inference, 
                3) multiscale Monte Carlo algorithm for high-resolution simulations, and 4) web-based visualizing tool. Using ChIA-PET data of human B-lymphocytes 
                (GM12878 cell line), we demonstrate the effectiveness of 3D-NOME in building 3D genome models at multiple levels, including the entire nucleome, 
                individual chromosomes, specific segments at megabase (Mb) and kilobase (kb) resolutions. We also consider CTCF-motif orientations and looping patterns 
                in order to achieve more reliable structures. Conclusions: 3D-NOME is an integrative computational pipeline that is effective in processing the 
                multifaceted ChIA-PET data for simulation of 3D genome from higher-order chromosome folding to detailed functional interactions mediated by protein 
                factors. Further refinement of 3D-NOME and application to additional ChIA-PET and other types of 3D genome mapping data will help to advance our 
                understanding of genome structures and functions.''',
    'header': 'Genome Structure, Variation, and Function',
    'year': int(2015)
}

po2015_3108T['content'] = re.sub(r'\s*\n\s*', ' ', po2015_3108T['content'])
po2015_3108T['authors'] = re.sub(r'\s*\n\s*', ' ', po2015_3108T['authors'])

po2015_3034T = {
    'id': '3034T', 
    'title': '2p15-p16. 1 microdeletions encompassing and proximal to BCL11A are associated with elevated HbF in addition to neurologic impairment.', 
    'authors': '''A. P. W. Funnell1, P. Prontera2, V. Ottaviani3, M. Piccione4, A. Giambona5, A. Maggio5, F. Ciaffoni6, S. Stehling-Sun1, 
                M. Marra6, F. Masiello6, L. Varricchio7, A. R. Migliaccio7,8, T. Papayannopoulou9, J. A. Stamatoyannopoulos1,10. 1) Department of 
                Genome Sciences, University of Washington, Seattle, WA; 2) Centro di Riferimento Regionale Genetica Medica, Azienda 
                Ospedaliera-Universitaria di Perugia, Perugia, Italy; 3) Genetica Medica, IRCCS “Ospedale Casa Sollievo della Sofferenza”, San Giovanni 
                Rotondo, Foggia, Italy; 4) Dipartimento Scienze per la promozione della salute e materno-infantile “G. D’Alessandro” Université degli Studi 
                di Palermo, Palermo 90127, Italy; 5) U. O. C. di Ematologia delle Malattie Rare del Sangue e degli Organi Emopoietici. AOOR Villa Sofia 
                Cervello, Palermo 90146, Italy; 6) Department of Biologia Cellulare and Neuroscience, Istituto Superiore Sanita, Viale Regina Elena 299, 
                00161 Rome, Italy; 7) Department of Medicine, Mount Sinai School of Medicine, New York, NY 10029, USA; 8) Department of Biomedical Sciences, 
                University of Bologna, via Irnerio 48, 40126 Bologna, Italy; 9) Division of Hematology, Department of Medicine, University of Washington, 
                Seattle, WA 98195, USA; 10) Division of Oncology, Department of Medicine, University of Washington, Seattle, WA 98195, USA.''',
    'content': '''-hemoglobinopathies, such as sickle cell anemia and -thalassemia, are amongst the most common genetic disorders worldwide. These diseases 
                arise from mutations that affect the function or expression of adult -globin (HBB). Treatment typically involves lifelong blood transfusion and 
                chelation therapy, with the only curative option being allogeneic transplantation of hematopoietic stem cells. However, it has long been known that 
                increased fetal hemoglobin (HbF) expression that persists into adulthood considerably ameliorates the clinical severity of these disorders. Reversing 
                the perinatal silencing of HbF has thus become a primary focus of therapeutic efforts. In recent years, the transcription factor BCL11A has emerged 
                as a key, and potent, repressor of HbF. Disrupting BCL11A function in an erythroid-specific fashion is rigorously being sought as a therapeutic option; 
                however, the potential impact of such disruption in humans has been unclear. This is due, in part, to the scarcity of reported mutations affecting the 
                coding region of BCL11A. Recently however, a number of patients have been described with shared neurodevelopmental defects arising from chromosome 
                2p15-p16. 1 microdeletions that variably cover segments of the BCL11A locus. Here, we have examined the hematological phenotype of three such patients 
                with distinct de novo microdeletions. All three display modestly reduced BCL11A expression in erythroblasts, and elevated HbF in peripheral blood 
                (approximately 5-10%). Interestingly, in one patient, the BCL11A coding gene is intact, with only a downstream region deleted. We have identified a number 
                of potential regulatory elements within this segment that are co-occupied by multiple principal erythroid transcription factors. We are currently employing 
                high throughput genome editing techniques to dissect the functionality of these candidate elements, with the anticipation that they might proffer attractive 
                targets for therapeutic intervention in the treatment of -hemoglobinopathies.''',
    'header': 'Genome Structure, Variation, and Function',
    'year': int(2015)
}

po2015_3034T['content'] = re.sub(r'\s*\n\s*', ' ', po2015_3034T['content'])
po2015_3034T['authors'] = re.sub(r'\s*\n\s*', ' ', po2015_3034T['authors'])

po2015_3070T = {
    'id': '3070T', 
    'title': 'Transcriptional consequences of 2q23. 1 deletion syndrome in iPSC-derived neural progenitor cells provide insight into neurodevelopmental disorders and autism.', 
    'authors': '''S. V. Mullegama1, S. R. Williams2, J. T. Alaimo1, L. Chen1,3, F. J. Probst1, C. Haldeman-Englert4, J. W. Innis5, P. Stankiewicz1, S. W. Cheung1, 
                T. Ezashi6, S. H. Elsea1. 1) Department of Molecular and Human Genetics, Baylor College of Medicine, One Baylor Plaza, Houston, TX, 77030, USA; 2) Center 
                for Public Health Genomics, University of Virginia, Charlottesville, VA 22902, USA; 3) Department of Cellular and Genetic Medicine, School of Basic Medical 
                Sciences, Fudan University, Shanghai 200032, China; 4) Fullerton Genetics Center, Asheville, NC 28803; 5) Departments of Human Genetics and Pediatrics and 
                Communicable Diseases, University of Michigan, Ann Arbor, MI 48109, USA; 6) Division of Animal Sciences, University of Missouri, Columbia, Missouri 65211, USA.''',
    'content': '''2q23. 1 deletion syndrome (2q23. 1 del) is a neurodevelopmental disorder in which haploinsufficiency of MBD5 is responsible for the core phenotype, which 
                includes intellectual disability (ID), autism spectrum disorder (ASD), seizures, speech impairment, motor delay, and sleep and behavioral problems. To comprehensively 
                understand the molecular role of MBD5 in early neuronal development, the 2q23. 1 del phenotype, and ASD, we generated neural progenitor cells (NPCs) derived from induced 
                pluripotent stem cells (iPSCs) that originated from 2q23. 1 del and age/ sex-matched control fibroblasts and performed transcriptome profiling by RNA-sequencing. Overall, 
                300 transcripts were differentially expressed as a consequence of reduced MBD5 dosage using Benjamini-Hochberg FDR (q<0. 05) analysis. Our transcriptome profile through 
                DAVID was enriched for neuronal development (P=0. 0002), neuronal migration (P=0. 0001), and neurogenesis (P=0. 00001). IPA identified a strong statistical enrichment for 
                pathways, including PTEN (P=0. 0003) and WNT signaling (P= 0. 003), which are critical contributors to neural stem cell and nervous system development. We identified genes 
                within our profile that are implicated in phenotypes present in 2q23. 1 del patients including ID (FMR1), seizures (SEZ6), speech impairment (FOXP2), motor delay (NR4A2), 
                and behavioral problems (ARTNL, HTR1B). Interestingly, 30% of our differentially expressed genes are associated with ASD as defined by the Simons Foundation and AutismKB 
                and are involved in essential cellular processes crucial in ASD pathogenesis including transcriptional regulation (MEF2C, FOXG1, NFIA), chromatin modification (CDH8, SIX1, 
                MEOX1), and neuronal function (NTNG1, GRIK2, LAMC3). In addition, when MBD5 is haploinsufficient, genes involved in phenotypically similar ASDs such as 5q14. 3 deletion 
                syndrome (MEF2C) and congenital variant of Rett syndrome (FOXG1) were dysregulated, suggesting that these genes function in a transcriptional cascade of common biological 
                networks that result in overlapping phenotypes. To identify possible novel deletion disorders, we queried our top 50 MBD5-down regulated genes, which were not linked to ASD 
                or OMIM disorders, through genome-wide aCGH databases and identified 17 candidate genes as possible disease causing genes. Overall, we demonstrate the multifactorial role of 
                MBD5 in the regulation of genes and pathways known to contribute to the genetic architecture of neurodevelopment and disease phenotypes.''',
    'header': 'Genome Structure, Variation, and Function',
    'year': int(2015)
}

po2015_3070T['content'] = re.sub(r'\s*\n\s*', ' ', po2015_3070T['content'])
po2015_3070T['authors'] = re.sub(r'\s*\n\s*', ' ', po2015_3070T['authors'])

pl2015_168 = {
    'id': int(168), 
    'title': 'A phenotype-aware approach to the prioritization of coding and non-coding rare disease variants.', 
    'authors': '''D. Smedley1, J. Jacobsen1, C. Mungall2, N. Washington2, S. Kohler3, S.E. Lewis2, M. Haendel4, P.N. Robinson3. 1) Wellcome Trust Sanger Institute, Cambridge, 
                United Kingdom; 2) Genomics Division, Lawrence Berkeley National Laboratory, Berkeley, CA 94720, USA; 3) Institute for Medical and Human Genetics, Charite-Universitatsmedizin, 
                Berlin, Germany; 4) University Library and Department of Medical Informatics and Epidemiology, Oregon Health & Sciences University, Portland, OR, USA.''',
    'content': '''Whole-exome sequencing has revolutionized rare disease research. However, many cases remain unsolved, in part because of the problem of prioritizing the ~100-1000 
                loss of function, candidate variants that remain after removing those deemed as common or non-pathogenic. We have developed the Exomiser suite of algorithms to tackle this through 
                additional use of patient phenotype data e.g. hiPHIVE assesses each candidate gene by comparing the patient phenotypes to existing phenotypic knowledge from disease and model organism 
                databases. For genes with missing data, a guilt-by-association approach is used based on the phenotypic similarity of near-by genes in a protein-protein association network. Benchmarking 
                on known HGMD mutations added to unaffected 1000 Genomes Project exomes, reveals the causative variant is detected as the top hit in 97% of samples and in 87% when phenotypic knowledge 
                of the known disease-gene association was masked to simulate novel disease gene discovery. Exomiser is being successfully applied to diagnosis and gene discovery in the Undiagnosed Disease 
                Program.However, many cases still remain unsolved after exome analysis and a significant fraction may be due to the presence of non-coding, causative variants. With many projects such as 
                the UK 100,000 Genomes Project adopting whole genome sequencing, the potential to detect such variants exists if scalable and accurate analysis tools are developed. We have extended hiPHIVE 
                to also assess variants in proximal and distal non-coding regions including tissue-specific enhancers. The predicted deleteriousness of these variants is assessed through combining measures 
                of conservation with indicators of regulatory regions such as DNase I hypersensitivity and transcription factor binding sites. Through manual curation of the literature, we have developed 
                a database of genotype and phenotype associations for several hundred regulatory mutations known to cause rare diseases. hiPHIVE was able to detect these regulatory mutations as the top 
                hit in 64% of samples when they were added to whole genomes from the 1000 Genomes Project. By variant category the performance was 55% for promoters, 79% for 5’UTR, 47% for 3’UTR, 100% for 
                microRNA genes and 57% for enhancers. Finally, this extension to non-coding variation paves the way for development of phenotype-aware analysis software for common disease.''',
    'header': 'ASHGAbstracts',
    'year': int(2015)
}

pl2015_168['content'] = re.sub(r'\s*\n\s*', ' ', pl2015_168['content'])
pl2015_168['authors'] = re.sub(r'\s*\n\s*', ' ', pl2015_168['authors'])

po2022_1537 = {
    'id': '1537', 
    'title': 'Molecular and clinical characterisation of Polish Temple syndrome patients with 14q32 alterations', 
    'authors': '''D. Jurkiewicz1, A. Madej-Pilarczyk1, A. Swiader-Lesniak2, K. Fraczak1, P. Halat-Wolska1, D. Siestrzykowska1, D. Piekutowska-Abramczuk1, M. Pelc1, B. Chalupczynska1, E. Ciara1 ,
                K. Chrzanowska1; 1 Dept. of Med. Genetics, The Children's Mem. Hlth.Inst., Warsaw, Poland, 2 Dept. of Anthropology, The Children's Mem. Hlth.Inst., Warsaw, Poland''',
    'content': '''Temple syndrome (TS14) is an imprinting disorder characterised by pre- and postnatal short stature with small hands and feet, muscular hypotonia and feeding problems in early infancy 
                followed by weight gain, premature puberty and in some cases speech delay and mild mental retardation. TS14 is caused by genetic/epigenetic abnormalities within the imprinted chromosomal region 14q32. 
                It may show overlapping phenotype with Silver-Russell syndrome (SRS). Here, we present clinical and molecular data of three patients with TS14. Molecular investigations were performed on leukocyte DNA 
                and included methylation sensitive multiplex ligation-dependent probe amplification (MS-MLPA) and microsatellite analyses (MSA). In two patients maternal UPD of chromosome 14 [upd(14)mat] was found and 
                in the third patient MEG3:TSS-DMR loss of methylation (LOM) was identified. Analysis of several imprinted loci in the patient with LOM excluded the presence of Multilocus Imprinting Disturbances (MLID). 
                Patients demonstrated typical clinical TS14 features, however in one patient with upd(14)mat mild intellectual disability was present. The investigations allowed to define the type of a 14q32 defect and 
                confirm the diagnosis of TS14 in examined patients. A complex molecular approach to analyse 14q32 region is required for accurate diagnosis of TS14 allowing the recurrence risk determination and proper 
                genetic counselling. The study corroborates that SRS should be considered in differential diagnosis with TS14 and shows efficacy of the applied diagnostic approach. The study was supported by CMHI project 
                S180/2019 and partly by MEiN projects: 7071/IB/SN/2020, 7088/II-KDM/SN/2020.''',
    'header': 'Complex Traits',
    'year': int(2022)
}

po2022_1537['content'] = re.sub(r'\s*\n\s*', ' ', po2022_1537['content'])
po2022_1537['authors'] = re.sub(r'\s*\n\s*', ' ', po2022_1537['authors'])

topic_mapping_2019 = {
    'Precision Medicine, Pharmacogenomics, and Genetic Therapies': (372, 505),
    'Prenatal, Perinatal, Reproductive, and Developmental Genetics': (506, 620),
    'Genetic Counseling, ELSI, Education, and Health Services Research': (621, 750),
    'Cancer Genetics': (751, 1082),
    'Mendelian Phenotypes': (1083, 1398),
    'Bioinformatics and Computational Approaches': (1399, 1746),
    'Molecular Phenotyping and Omics Technologies': (1747, 1886),
    'Complex Traits and Polygenic Disorders': (1887, 2297),
    'Evolution and Population Genetics': (2298, 2410),
    'Molecular and Cytogenetic Diagnostics': (2411, 2617),
    'Cardiovascular Phenotypes': (2618, 2793),
    'Statistical Genetics and Genetic Epidemiology': (2794, 3063),
    'Molecular Effects of Genetic Variation': (3064, 3212),
    'Epigenetics and Gene Regulation': (3213, 3364),
}

parsers = {
    range(2013, 2019): parser_13_to_18,
    2022: parser_22
}

def assign_topic_2019(id):
    for topic, (start, end) in topic_mapping_2019.items():
        if start <= int(id) <= end:
            return topic
    return None

def get_parser(year):
    for year_range, parser in parsers.items():
        if isinstance(year_range, range):
            if year in year_range:
                return parser
        elif year == year_range:
            return parser
    return None


for filename in os.listdir(PDF_FOLDER_PATH):
    if filename.endswith('pdf') and not any(sub_str in filename for sub_str in ['2015', '2019', '2021', '2023', '2022-Poster']):
        match = re.search(r'(\d{4})', filename)
        if match:
            year = int(match.group(1))
            file_path = os.path.join(PDF_FOLDER_PATH, filename)
            var_name = os.path.splitext(filename)[0]
            parser = get_parser(year)

            if parser:
                logging.info(f'Processing {filename}')
                file = fitz.open(file_path)
                df = parser(file)
                df = df[df['content'].notnull()]
                df['year'] = year
                csv_path = os.path.join(CSV_FOLDER_PATH, f'{var_name}.csv')
                df.to_csv(csv_path, index=False, escapechar='\\')
                logging.info(f'Saved DataFrame to {csv_path}')
            else:
                logging.info(f'No parser found for {filename}')
        else:
            logging.info(f'Skipping {filename} (No year found)')

pl2015_file = fitz.open(os.path.join(PDF_FOLDER_PATH, '2015-platform-abstracts-min.pdf'))
po2015_file = fitz.open(os.path.join(PDF_FOLDER_PATH, '2015-poster-abstracts.pdf'))

pl2015_df = parser_13_to_18(pl2015_file)
po2015_df = parser_13_to_18(po2015_file)

pl2015_df['year'] = int(2015)
po2015_df['year'] = int(2015)

po2015_df.set_index('id', inplace=True)
pl2015_df.set_index('id', inplace=True)

po2015_df.update(pd.DataFrame([po2015_1885W, po2015_3108T, po2015_3034T, po2015_3070T]).set_index('id'))
pl2015_df.update(pd.DataFrame([pl2015_168]).set_index('id'))

po2015_df.reset_index(inplace=True)
pl2015_df.reset_index(inplace=True)

pl2015_df.to_csv(os.path.join(CSV_FOLDER_PATH, '2015-platform-abstracts-min.csv'), index=False, escapechar='\\')
po2015_df.to_csv(os.path.join(CSV_FOLDER_PATH, '2015-poster-abstracts.csv'), index=False, escapechar='\\')



pl2019_file = fitz.open(os.path.join(PDF_FOLDER_PATH, 'ASHG-2019-platform-plenary-abstracts.pdf'))
po2019_file = fitz.open(os.path.join(PDF_FOLDER_PATH, 'ASHG-2019-poster-abstracts.pdf'))

pl2019_df = parser_19(pl2019_file)
po2019_df = parser_19(po2019_file)

pl2019_df['year'] = int(2019)
po2019_df['year'] = int(2019)

po2019_df['header'] = po2019_df['id'].apply(assign_topic_2019)

pl2019_df.to_csv(os.path.join(CSV_FOLDER_PATH, 'ASHG-2019-platform-plenary-abstracts.csv'), index=False, escapechar='\\')
po2019_df.to_csv(os.path.join(CSV_FOLDER_PATH, 'ASHG-2019-poster-abstracts.csv'), index=False, escapechar='\\')



p2021_file = fitz.open(os.path.join(PDF_FOLDER_PATH, '2021-ASHG-Meeting-Abstracts.pdf'))

p2021_dfs = parser_21(p2021_file)
p2021_suffixes = ['Plenary', 'Platform', 'Talks', 'Presentations']
for p2021_df, suffix in zip(p2021_dfs, p2021_suffixes):
    p2021_df['year'] = int(2021)
    p2021_df.to_csv(os.path.join(CSV_FOLDER_PATH, f'2021-ASHG-Meeting-Abstracts-{suffix}.csv'), index=False, escapechar='\\')



po2022_file = fitz.open(os.path.join(PDF_FOLDER_PATH, 'ASHG2022-PosterAbstracts.pdf'))

po2022_df = parser_22(po2022_file)

po2022_df['year'] = int(2022)

po2022_df.set_index('id', inplace=True)

po2022_df.update(pd.DataFrame([po2022_1537]).set_index('id'))

po2022_df.reset_index(inplace=True)

po2022_df.to_csv(os.path.join(CSV_FOLDER_PATH, 'ASHG2022-PosterAbstracts.csv'), index=False, escapechar='\\')


pla2023_file = fitz.open(os.path.join(PDF_FOLDER_PATH, 'ASHG2023-PlatformAbstracts.pdf'))
ple2023_file = fitz.open(os.path.join(PDF_FOLDER_PATH, 'ASHG2023-PlenaryAbstracts.pdf'))
po2023_file = fitz.open(os.path.join(PDF_FOLDER_PATH, 'ASHG2023-PosterAbstracts.pdf'))

pla2023_df = parser_23_non_poster(pla2023_file)
ple2023_df = parser_23_non_poster(ple2023_file)
po2023_df = parser_23_poster(po2023_file)

pla2023_df['year'] = int(2023)
ple2023_df['year'] = int(2023)
po2023_df['year'] = int(2023)

pla2023_df.to_csv(os.path.join(CSV_FOLDER_PATH, 'ASHG2023-PlatformAbstracts.csv'), index=False, escapechar='\\')
ple2023_df.to_csv(os.path.join(CSV_FOLDER_PATH, 'ASHG2023-PlenaryAbstracts.csv'), index=False, escapechar='\\')
po2023_df.to_csv(os.path.join(CSV_FOLDER_PATH, 'ASHG2023-PosterAbstracts.csv'), index=False, escapechar='\\')



recat_dict = {
    'Developmental Genetics and Gene Function': 'Developmental Genetics',
    'Genetic Counseling': 'Genetic Counseling',
    'Complex Traits': 'Complex Traits and Polygenic Disorders',
    'Complex Traits and Polygenic Disorders': 'Complex Traits and Polygenic Disorders',
    'Bioinformatics and Computational Approaches': 'Bioinformatics',
    'Pharmacogenomics': 'PGx',
    'Cardiovascular Diseases': 'Cardiology',
    'Prenatal, Perinatal, and Reproductive Genetics': 'Reproductive genetics',
    'Psychiatric Genetics, Neurogenetics and Neurodegeneration': 'Psychiatric Genetics, Neurogenetics and Neurodegeneration',
    'Statistical Genetics and Genetic Epidemiology': 'Statistical Genetics and Genetic Epidemiology',
    'Epigenetics and Gene Regulation': 'Epigenetics',
    'Molecular Phenotyping and Omics Technologies': 'To split',
    'Bioinformatics and Genomic Technology': 'Bioinformatics',
    'Molecular Effects of Genetic Variation': 'Genetic Variation',
    'Pharmacogenetics': 'PGx',
    'Cytogenetics': 'Cytogenetics',
    'Prenatal, Perinatal, Reproductive, and Developmental Genetics': 'To split',
    'Cancer': 'Cancer',
    'Evolution and Population Genetics': 'Evolution and Population Genetics',
    'Clinical Genetics and Dysmorphology': 'Clinical Genetic Testing',
    'Evolutionary and Population Genetics': 'Evolution and Population Genetics',
    'Prenatal, Perinatal, and Developmental Genetics': 'To split',
    'Epigenetics': 'Epigenetics',
    'Genome Structure, Variation, and Function': 'To split',
    'Genome Structure, Variation and Function': 'To split',
    'Genome Structure and Function': 'Genome Structure and Function',
    'Ethical, Legal, Social and Policy Issues in Genetics': 'ELSI',
    'Psychiatric Genetics, Neurogenetics, and Neurodegeneration': 'Psychiatric Genetics, Neurogenetics and Neurodegeneration',
    'Health Services Research': 'Health Services Research',
    'Cancer Genetics': 'Cancer',
    'Development': 'Developmental Genetics',
    'Prenatal, Perinatal and Reproductive Genetics': 'Reproductive genetics',
    'Ethical, Legal, Social, and Policy Issues in Genetics': 'ELSI',
    'Therapy for Genetic Disorders': 'Therapy for Genetic Disorders',
    'Cardiovascular Phenotypes': 'Cardiology',
    'Molecular and Cytogenetic Diagnostics': 'Clinical Genetic Testing',
    'Clinical Genetic Testing': 'Clinical Genetic Testing',
    'Genetic Counseling, ELSI, Education, and Health Services Research': 'To split',
    'Genetic Therapies': 'Therapy for Genetic Disorders',
    'Mendelian Phenotypes': 'Mendelian Phenotypes',
    'Precision Medicine, Pharmacogenomics, and Genetic Therapies': 'To split',
    'Genetic Counseling, ELSI, Education, and Health Services': 'To split',
    'Late Breaking Posters on COVID-19': 'COVID-19',
    'Genetic, Genomic, and Epigenomic Resources and Databases': 'Resources',
    'Genetics/Genomics Education': 'Education',
    'Cardiovascular Genetics': 'Cardiology',
    'Genetic, Genomic, and Epigenomic Annotations, Databases and Resources': 'Resources',
    'Molecular Basis of Mendelian Disorders': 'Mendelian Phenotypes',
    'Omics Technologies': 'Omics Technologies',
    'Metabolic Disorders': 'Clinical Genetic Testing'
    }

poster_dfs = []
for filename in os.listdir(CSV_FOLDER_PATH):
    if 'poster' in filename.lower():
        csv_path = os.path.join(CSV_FOLDER_PATH, filename)
        df = pd.read_csv(csv_path)
        truncated_df = df[['title', 'content', 'header', 'year']]
        poster_dfs.append(truncated_df)

poster_df = pd.concat(poster_dfs, ignore_index=True)
poster_df['header'] = poster_df ['header'].replace(recat_dict)
training_data = poster_df[~poster_df['header'].isin(['To split', 'COVID-19'])]
training_data.to_csv(os.path.join(DATA_FOLDER_PATH, 'training_data.csv'))