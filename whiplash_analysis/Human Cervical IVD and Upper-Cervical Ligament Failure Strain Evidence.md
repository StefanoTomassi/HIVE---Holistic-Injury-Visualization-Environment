# Human Cervical IVD and Upper-Cervical Ligament Failure Strain Evidence
## Executive answer
The literature search did **not identify a direct, tissue-level human cervical failure strain separately measured for nucleus pulposus (NP) and annulus fibrosus (AF)**. The closest human cervical evidence is structural rather than constituent-level: (1) Yoganandan et al. tested isolated cervical disc units in axial tension and reported failure load and distraction; and (2) Ivancic et al. tested a coronal **middle-third disc** bone–disc–bone strip dynamically to rupture and reported peak elongation, but neither paper resolves NP from AF nor supplies a defensible local AF/NP strain threshold.[^1][^2][^3]

For the upper cervical spine, a much better source exists: Mattucci’s 2011 thesis reports engineering failure strain for the transverse ligament, AAOM, PAOM, and a combined tectorial membrane–vertical cruciate–apical–alar complex at quasi-static and impact-relevant rates. However, it does **not** isolate the tectorial membrane, vertical cruciate bands, apical ligament, or alar ligaments within that complex, so the complex value must not be assigned independently to each constituent.[^4][^5]
## Scope and definitions
This review distinguishes three quantities that are often conflated:

- **Local material failure strain**: strain measured within a tissue coupon or constituent, with a defined strain measure and gauge length.
- **Structural engineering strain**: change in grip-to-grip or insertion-to-insertion length divided by initial length for a bone–soft-tissue–bone preparation.
- **Failure distraction/elongation**: displacement at structural failure; this is not strain unless the relevant initial length is known and the deformation field is sufficiently uniform.

The distinction is critical for IVDs because an intact disc is a pressurized, heterogeneous composite of NP, AF, and cartilaginous endplates. NP normally functions predominantly through pressure and fluid-solid interaction, while AF carries anisotropic tension; therefore, one scalar “NP tensile failure strain” is not generally an experimentally natural or transferable injury variable.[^6][^7]
## Human cervical IVD evidence
### Direct structural tests
| Study | Human cervical preparation | Rate/loading | Reported failure result | What it supports | Main limitation |
|---|---|---|---|---|---|
| Yoganandan et al., 1996, *Human head-neck biomechanics under axial tension* | 20 isolated C2–T1 intervertebral-disc units from 8 cadavers; posterior structures sequentially removed so the disc remained in situ | Axial tension; slow-rate category in Ivancic’s review | Mean failure load **569 N** and failure distraction **11.1 mm**; failure occurred at the disc–endplate junction without vertebral fracture[^1][^2][^3] | Best direct human cervical **whole-disc structural tensile tolerance** located in this search | No AF/NP separation; no local strain field; the reported failure site is an interface, so converting distraction to “AF failure strain” would be unsafe |
| Ivancic et al., 2007, *Dynamic Mechanical Properties of Intact Human Cervical Spine Ligaments* | 11 “middle-third disc” (MTD) bone–disc–bone specimens, C2–T1, from 6 spines, mean age 80.6 years | Mean peak elongation rate **723 ± 106 mm/s** | Peak force **115.6 ± 79.9 N**; peak elongation **2.1 ± 0.9 mm**; energy **0.12 ± 0.15 J**; stiffness 61.3, 81.4 and 96.0 N/mm at 25%, 50% and 75% peak force[^3] | Dynamic failure curve for a human cervical central disc strip, including both NP/AF-region tissues and end attachments | MTD was made by coronally sectioning the anterior elements into thirds; it is not isolated NP or AF. No initial gauge length or local strain was reported, and fiber-axis alignment was difficult[^3] |

Ivancic’s modeled physiological MTD elongation was only **0.3 mm** (range defined as mean ±2 SD: 0.1–0.5 mm), while experimental peak elongation averaged 2.1 mm; the authors described this as a structural safety-factor comparison, not a material strain threshold.[^3]
### Why no NP failure strain emerged
Human NP experiments located in the search characterize confined/unconfined compression, shear, swelling pressure, aggregate modulus, and permeability rather than rupture. For example, non-degenerate human NP had equilibrium toe- and linear-region moduli of **3.25 ± 1.56 kPa** and **5.39 ± 2.56 kPa** in unconfined compression, but no failure criterion was obtained. Recent human cervical tissue work likewise reports cervical NP and AF biphasic properties—e.g., cervical NP aggregate modulus **0.44 ± 0.44 MPa**—and explicitly calls for future cervical tensile characterization.[^8][^7]

This gap is mechanically plausible: a hydrated healthy NP relaxes shear stress toward zero and acts mainly as a pressurized fluid-rich solid, while clinically recognizable NP “failure” usually manifests through AF/endplate failure and loss of containment rather than rupture of an isolated NP coupon. Cell-stretch thresholds such as 5–10% “physiological” and >15–20% “pathological” describe mechanobiological responses in culture, not gross human NP rupture, and should not be used as FE element-deletion strains.[^9][^7][^10]
### Transfer evidence for AF
Direct human AF coupon failure data exist predominantly for **lumbar**, not cervical, tissue. A broad review of human AF tensile tests gives an average circumferential failure strain around **0.30**, with individual reported averages spanning roughly **0.12–0.80** depending on orientation, specimen architecture, and protocol; along-fiber multilamellar failure was summarized as approximately **0.25**. Galante’s classic human lumbar work has also been interpreted as an annular-fiber elastic limit of approximately **31.5% ± 1.5%**, while later studies report highly orientation-dependent failure stretches, about 1.15 circumferentially and 1.8 radially in the cited protocols.[^11][^12][^13][^14]

These lumbar values are useful as **sensitivity-analysis priors**, not validated cervical criteria. Cervical posterior AF architecture differs from lumbar AF, and a cervical-specific fatigue model explicitly stated that lumbar AF tensile strength was the most relevant evidence available because cervical failure data could not be found. Human lumbar datasets further show substantial effects of radial position, region, and degeneration; one large study reported failure elongation decreasing from about **49% in inner AF to 38% in outer AF**.[^15][^16][^17][^18]
### Practical IVD recommendation
For a cervical FE model, the most defensible hierarchy is:

1. **Whole-disc structural validation:** use Yoganandan’s 569 N / 11.1 mm isolated-disc response as a tensile structural target, with the caveat that the observed failure was at the disc–endplate junction.[^1][^2]
2. **Dynamic central-strip validation:** use Ivancic’s MTD force–elongation response, especially 115.6 N and 2.1 mm at peak force, as an independent dynamic target for a coronal central-third specimen—not as NP or AF material strain.[^3]
3. **AF damage sensitivity range:** if a strain-driven AF criterion is unavoidable, explore lumbar-human priors rather than selecting one universal number: approximately 0.25–0.30 for circumferential/fiber-dominated tensile rupture, while explicitly testing broader orientation-dependent values reported in the human AF literature.[^11][^12][^13]
4. **NP formulation:** avoid element deletion from a single “failure strain.” Model containment loss through AF/endplate/cohesive failure and allow NP extrusion/pressure loss. A separate NP rupture value could not be substantiated from human cervical experiments.

No subfailure cervical AF injury threshold analogous to ligament subfailure-strain studies was verified. Physiological or simulated AF strains and cellular catabolic thresholds describe different endpoints and cannot be relabeled as macroscopic tissue injury thresholds.[^19][^20][^10]
## Upper-cervical failure strains
### Best unified dataset
Mattucci’s 2011 MASc thesis is the most directly useful source found for engineering strain-to-failure across the requested craniovertebral structures. Specimens were preconditioned for 20 cycles at 10% strain, kept in an environmental chamber intended to reproduce in-vivo temperature and humidity, and failed at quasi-static **0.5 s⁻¹** or high **150 s⁻¹** rates.[^4][^5]

| Structure tested | Preparation and n | Failure strain at 0.5 s⁻¹ | Failure strain at 150 s⁻¹ | Toe-region strain | Interpretation |
|---|---:|---:|---:|---:|---|
| TM complex | Tectorial membrane + vertical cruciate + apical + alar ligaments; n=8 (3 quasi, 5 high) | **0.43 ± 0.10** | **0.27 ± 0.04** | 0.07 ± 0.01 quasi; 0.07 ± 0.02 high | Rate effect on failure strain was significant (p=0.04); valid only for the combined complex[^4][^5] |
| Transverse ligament (horizontal cruciform component) | Isolated TL; n=6 (2 quasi, 4 high) | **0.25 ± 0.08** | **0.26 ± 0.03** | 0.10 ± 0.03 quasi; 0.12 ± 0.02 high | Closest direct value for the load-bearing transverse part of the cruciform ligament[^4][^5] |
| AAOM | Each broad membrane divided into left/right halves; n=14 (6 quasi, 8 high) | **0.46 ± 0.10** | **0.49 ± 0.16** | 0.14 ± 0.07 quasi; 0.11 ± 0.04 high | Half-membrane test; values are material-style engineering strain, but force cannot be compared directly with a full membrane[^4][^5] |
| PAOM | Each broad membrane divided into left/right halves; n=14 (6 quasi, 8 high) | **0.52 ± 0.13** | **0.39 ± 0.20** | 0.11 ± 0.06 quasi; 0.08 ± 0.05 high | Larger scatter, especially dynamically; rate effect on failure strain not significant[^4][^5] |
| AAAM | Single specimen | **0.53** | — | 0.08 | n=1; descriptive only[^5] |
| PAAM | Single specimen | **0.49** | — | 0.09 | n=1; descriptive only[^5] |

Associated mean failure forces from Mattucci were: TM complex **1006 ± 416 N** quasi-static and **1582 ± 370 N** high-rate; TL **534 ± 116 N** and **423 ± 76 N**; AAOM **516 ± 192 N** and **509 ± 108 N**; PAOM **198 ± 80 N** and **162 ± 52 N**. Because AAOM and PAOM were tested as halves, force values must match the modeled representation before direct use.[^5][^4]
### Alar ligament
Panjabi et al. directly tested fresh human unilateral alar and transverse ligaments slowly to a prescribed subfailure load and then dynamically to failure at **920 mm/s**. For the alar ligament, strain at 70 N changed from **16.4%** during slow extension to **0.3%** during fast extension; dynamic failure occurred at mean strain **3.1%**, force **367 N**, and absorbed energy **123 N·mm**. A later craniocervical review independently summarizes this result as mean failure strain about **3%** and failure load **367 ± 83.2 N**.[^21][^22]

This 3.1% value conflicts strongly with Mattucci’s 27% high-rate TM-complex failure strain, but they are not measurements of the same structure or protocol. Panjabi tested an isolated unilateral alar bone–ligament–bone specimen at 920 mm/s after a prior slow loading step, whereas Mattucci tested a much larger multi-ligament complex at 150 s⁻¹, with a different initial length and sequential constituent recruitment. Therefore:[^4][^21]

- For an **individually represented alar ligament**, Panjabi’s **0.031 mean dynamic failure strain** is the direct source.
- For a **lumped TM/vertical cruciate/apical/alar representation**, Mattucci’s **0.27 ± 0.04 at 150 s⁻¹** is structurally consistent.
- Do not mix Panjabi’s isolated-alar failure force with Mattucci’s complex failure strain in one material card.
### Cruciform ligament
The cruciform ligament comprises the transverse ligament and superior/inferior vertical bands; the vertical component is relatively weak and contributes little discernible craniocervical stability. The search found a direct strain value for the **transverse component** in Mattucci (approximately 0.25–0.26), but no isolated human failure strain for the superior and inferior vertical cruciate bands. Mattucci included the vertical cruciate component inside the TM complex, so **0.43 quasi-static / 0.27 high-rate** cannot be assigned specifically to the vertical bands.[^4][^5][^23]

A separate elderly C1–C2 flexion study measured transverse-ligament strain with gauges and reported failure at **2102.9 µm/m** with mean force **175 N**. Numerically that strain is only about 0.00210, far below isolated-ligament engineering failure strains, suggesting it is a local surface strain-gauge reading in an intact bending setup rather than a transferable insertion-to-insertion ligament failure strain; it should not replace Mattucci’s material-style tensile values.[^24]
### Tectorial membrane
No isolated human tectorial-membrane material failure strain was found. Mattucci’s TM-complex result is the closest quantitative tensile threshold but combines TM with vertical cruciate, apical, and alar structures. The dedicated anatomical/biomechanical study of the TM reported that it became taut at approximately 15° flexion and 20° extension and acted as a hammock over the dens after alar and transverse sectioning, but did not report strain-to-failure.[^25][^4][^5]
### AAOM and PAOM
Mattucci provides the direct values recommended for separate AAOM and PAOM FE parts. The 2013 journal article based on craniovertebral testing confirms that 54 ligaments from 21 spines were failed in tension at **0.5 s⁻¹** and **150 s⁻¹**, including transverse, AAOM, PAOM, Skull–C1/C1–C2 capsules, AAAM, PAAM, and the TM/vertical-cruciate/apical/alar complex; its abstract reports rate effects but not the full strain table, making the thesis the necessary numerical source.[^26][^27][^4]
## Suggested FE implementation
| FE part | Preferred evidence | Suggested interpretation |
|---|---|---|
| Cervical AF fibers | Human lumbar coupon data only as proxy | Run uncertainty/sensitivity cases around 0.25–0.30 for fiber-dominated circumferential rupture; use direction- and architecture-specific calibration rather than universal deletion[^11][^12] |
| AF ground substance/interlamellar interfaces | No human cervical strain threshold found | Use continuum/cohesive damage calibrated to whole-disc response and desired failure mode; do not assign the fiber threshold to matrix or interfaces |
| NP | No verified human cervical rupture strain | Do not use a scalar rupture strain; couple failure to containment loss, pressure loss, cavitation/contact, or AF/endplate damage |
| Whole cervical disc validation | Yoganandan 1996 | Target approximately 569 N and 11.1 mm in the replicated isolated-disc axial-tension setup, including interface failure[^1][^2] |
| Dynamic central disc strip | Ivancic 2007 | Target 115.6 ± 79.9 N and 2.1 ± 0.9 mm for the replicated middle-third strip test[^3] |
| Alar | Panjabi 1998 | Mean dynamic failure engineering strain 0.031 at 920 mm/s; retain protocol dependence[^21][^22] |
| Transverse cruciform band | Mattucci 2011 | Failure strain 0.25 ± 0.08 at 0.5 s⁻¹ and 0.26 ± 0.03 at 150 s⁻¹[^4][^5] |
| Vertical cruciate bands | No isolated value | Keep separate uncertainty; do not automatically inherit transverse-band or TM-complex values |
| AAOM | Mattucci 2011 | 0.46 ± 0.10 quasi-static; 0.49 ± 0.16 high-rate[^4][^5] |
| PAOM | Mattucci 2011 | 0.52 ± 0.13 quasi-static; 0.39 ± 0.20 high-rate[^4][^5] |
| Tectorial membrane | No isolated value | If modeled in a lumped complex, use 0.43 ± 0.10 quasi-static / 0.27 ± 0.04 high-rate; if isolated, treat this only as a complex-level upper validation target[^4][^5] |

For LS-DYNA implementation, failure values should be paired with the same strain measure used by the material formulation. Mattucci and Panjabi report nominal/engineering strain based on length change; these values should not be entered unmodified as Green–Lagrange strain, logarithmic strain, or maximum-principal element strain. At large extension, conversions matter: engineering strain 0.49 corresponds to stretch 1.49, logarithmic strain approximately 0.40, and Green–Lagrange strain approximately 0.61 under homogeneous uniaxial deformation.
## Evidence gaps
The strongest conclusion is a negative one: **there is no currently verified direct human cervical AF-and-NP constituent failure-strain dataset in the sources located**, despite whole-disc and central-strip failure experiments. This agrees with recent cervical disc work calling for tensile characterization and with cervical AF damage models that resort to lumbar human strength data.[^8][^18]

The upper-cervical evidence is sufficient for AAOM, PAOM, transverse ligament, and isolated alar at specific rates, but remains incomplete for **isolated tectorial membrane and isolated vertical cruciate bands**. Future testing should use full-field optical strain, clearly report reference configuration and strain measure, preserve physiologic hydration/preload, and separate midsubstance rupture from enthesis or bone failure.

---

## References

1. [Human head-neck biomechanics under axial tension](https://www.sciencedirect.com/science/article/pii/1350453395000542) - experimental 
...
human 
...
in these
...
biomechanical 
parameters

2. [Human head-neck biomechanics under axial tension](https://www.sciencedirect.com/science/article/pii/1350453395000542/pdf?md5=50d66121dec564ef9a9449e56c9588d6&pid=1-s2.0-1350453395000542-main.pdf) - Human head-neck biomechanics under axial tension
...
8.9 mm,

3. [Dynamic Mechanical Properties of Intact Human Cervical ...](https://pmc.ncbi.nlm.nih.gov/articles/PMC2729587/) - di PC Ivancic · 2007 · Citato da 100 — The present study determined the tensile mechanical propertie...

4. [Strain Rate Dependent Properties of Younger Human Cervical ...](https://uwspace.uwaterloo.ca/items/43cccf45-7cea-4c31-b07a-d738c6399d2b) - di S Mattucci · 2011 · Citato da 226 — The objective of this research was to provide detailed mechan...

5. [Strain Rate Dependent Properties of Human Cervical Spine ...](https://uwspace.uwaterloo.ca/bitstream/handle/10012/6259/Mattucci_Stephen.pdf;jsessionid=0C394DD3DC1F8C44C5D6447E52069605?sequence=1) - di S Mattucci · 2011 · Citato da 219 — The objective of this research was to provide detailed mechan...

6. [Anatomy, Back, Intervertebral Discs - StatPearls - NCBI - NIH](https://www.ncbi.nlm.nih.gov/books/NBK470583/) - The IVD functions as a heterogeneous composite structure that enables spinal flexibility while trans...

7. [Material properties in unconfined compression of human nucleus ...](https://pmc.ncbi.nlm.nih.gov/articles/PMC2223355/) - Proper function of the NP involves lateral expansion under axial compressive loads, thereby putting ...

8. [Characterizing the Baseline Regional Biphasic Mechanical ...](https://pmc.ncbi.nlm.nih.gov/articles/PMC12391200/) - A previously established confined compression testing technique was used to measure swelling pressur...

9. [The viscoelastic behavior of the non-degenerate human lumbar nucleus pulposus in shear](https://www.sciencedirect.com/science/article/pii/S0021929097000699) - stress-relaxation 
tests, the shear stress of the nucleus 
...
of the tissue.

10. [Cyclic tensile loading regulates nucleus pulposus cell autophagy ...](https://link.springer.com/article/10.1186/s12967-026-07932-6?error=cookies_not_supported&code=77702e4e-bfe7-453b-9a60-c49e3e7a2fb3) - While 5–10% strain is broadly considered physiological and > 15% strain is commonly used to denote p...

11. [[PDF] Biomechanics of the human intervertebral disc - QUT ePrints](https://eprints.qut.edu.au/103284/14/__qut.edu.au_Documents_StaffHome_staffgroupW$_wu75_Documents_ePrints_103284.pdf) - The maximum strain rate at which the tensile behaviour of the AF has been investigated is 4%/s which...

12. [[PDF] Biomechanics of the human intervertebral disc_ A review of testing ...](https://research-information.bris.ac.uk/ws/portalfiles/portal/106096608/1_s2.0_S1751616117300449_main.pdf) - In circumfer- ential tension the average failure stress was 2.7 MPa and the average failure strain w...

13. [PII: 0021-9290(85)90012-0](https://deepblue.lib.umich.edu/bitstream/handle/2027.42/25913/0000476.pdf;sequence=1) - data suggested 
that the 
elastic limit for annular fibers is approximately

14. [Application of a fiber-reinforced continuum theory to multiple deformations of the annulus fibrosus](https://www.sciencedirect.com/science/article/abs/pii/S0021929099001086) - Weidenbaum, M., 1995.
Degeneration and aging a!ect the tensile behavior of human lumbar anulus "bros...

15. [link.springer.com · article · 10Correlation between biomechanical properties of the annulus ...](https://link.springer.com/article/10.1007/s00586-015-4061-4) - 44 human cadaveric lumbar spines were harvested (24 male, 20 female, aged 25–64 years).
...
1969 spe...

16. [link.springer.com · content · pdfCorrelation between biomechanical properties of the annulus ...](https://link.springer.com/content/pdf/10.1007/s00586-015-4061-4.pdf) - 1969 specimens from 189 discs were stretched to failure.
Average tensile stiffness (modulus) increas...

17. [Annulus fibrosus | Radiology Reference Article | Radiopaedia.org](https://radiopaedia.org/articles/annulus-fibrosus) - 4. Unlike the nucleus pulposus, on which mainly compressive forces act, the fibers of the annulus fi...

18. [A non-linear multiaxial fatigue damage model for the cervical intervertebral disc annulus - Shruti Motiwale, Adhitya Subramani, Reuben H Kraft, Xianlian Zhou, 2018](https://journals.sagepub.com/doi/10.1177/1687814018779494) - ^15^ Having also conducted tensile failure tests on vertical slices of lumbar intervertebral discs, ...

19. [Mechanisms of Cervical Spine Disc Injury under Cyclic Loading - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6147880/) - Here, we developed a finite element model of the human C4–C5 disc.

20. [STUDY DESIGN](https://stacks.cdc.gov/view/cdc/33288/cdc_33288_DS2.xml) - PC
...
MP
...
Dynamic mechanical properties of intact human cervical spine ligaments

21. [The mechanical properties of human alar and transverse ...](https://pubmed.ncbi.nlm.nih.gov/11415778/) - At 70 N, the average alar ligament strain decreased from 16.4 to 0.3%, the stiffness increased from ...

22. [Update on the Biomechanics of the Craniocervical Junction, Part II: Alar Ligament](https://pmc.ncbi.nlm.nih.gov/articles/PMC8351059/) - The mean strain when the alar ligament failed was 3%, the mean energy absorbed was 122.6 N mm, and t...

23. [The craniocervical junction: embryology, anatomy ... - PMC - NIH](https://pmc.ncbi.nlm.nih.gov/articles/PMC5265194/) - Tears of the transverse ligament typically occur laterally at the attachment to the tubercle on the ...

24. [The role of the transversal ligament on the atlantoaxial complex - Bending forces at C1/2 flexion limits in the elderly - PubMed](https://pubmed.ncbi.nlm.nih.gov/33765570/) - In four out of five, a rupture of the transverse atlantal ligament was observed, the mean force requ...

25. [The tectorial membrane: Anatomical, biomechanical, and histological analysis](https://onlinelibrary.wiley.com/doi/pdf/10.1002/ca.20334) - With the alar and transverse ligaments cut and with flexion of the head, the middle portion of this ...

26. [Strain rate dependent properties of human craniovertebral ...](https://pubmed.ncbi.nlm.nih.gov/23665484/) - Fifty-four craniovertebral ligaments were isolated from twenty-one spines, and tested to failure in ...

27. [Strain rate dependent properties of human craniovertebral ligaments](https://www.sciencedirect.com/science/article/abs/pii/S1751616113001276) - Strain rate dependent properties of human craniovertebral ligaments
...
05/14/2013

