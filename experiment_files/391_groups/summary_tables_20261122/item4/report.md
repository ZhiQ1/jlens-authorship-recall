# Item 4 — meaning of the leading name-position PCs at L48 (exploratory, post hoc)

Exploratory (post hoc, not pre-registered), 2026-11-22. CPU only, stored states.
Item 4 (L48): meaning of the leading PCs of the name-position title-specific vectors d_i (surname first token, Vpd usable
  false titles; raw/b2_npprobe; same d_i as explore_pca_np_20261120.py). PCA = centered PCA of pooled paper-mean d
  (target + control) so that target share is a feature. For PCs 1-30: top-20 and bottom-20 papers by score; features of each
  20-set: papers sharing an author team with another paper in the set, papers sharing the first author (full-name string),
  modal field share, mean year, mean log10(1+citations), target share, mean title word count, modal share of the first
  author's surname-first token. Enrichment vs 2,000 random 20-sets from the same papers (one-sided upper for count/mode
  features, two-sided for means); Holm over 30 PCs x 2 ends x 8 features.


Pooled papers 4654 (target 3130, control 1524); PC1–30 variance shares: 0.066, 0.050, 0.044, 0.031, 0.030, 0.025, 0.022, 0.021, 0.020, 0.017, 0.017, 0.016, 0.014, 0.013, 0.012, 0.012, 0.011, 0.010, 0.010, 0.009, 0.009, 0.008, 0.008, 0.008, 0.007, 0.007, 0.007, 0.007, 0.006, 0.006

## Holm-significant features (p_holm < 0.05): 0 of 480 tests
| pc | var_share | end | feature | value | null_mean | p | modal_field | p_holm |
|---|---|---|---|---|---|---|---|---|

## Example titles (first 3 of each 20-set)
| pc | end | examples |
|---|---|---|
| 1 | top | The birth of topological insulators || Gain and plasmon dynamics in active negative-index metamaterials || Symmetry and density-functional exchange and correlation |
| 1 | bottom | What is a case study? || Student factors related to learning in biomechanics || The channelization of upper and lower anterior face heights compared t |
| 2 | top | The ABCs of depression: integrating affective, biological, and cogniti || Mortality from pandemic A/H1N1 2009 influenza in England: public healt || The Contribution of Primordial Binaries to the Blue Straggler Populati |
| 2 | bottom | Drug-DNA interactions and their study by UV-Visible, fluorescence spec || Titanium-added praseodymium silicate high-k layers on Si(001) || Development of an algorithm to measure defect geometry using a 3D lase |
| 3 | top | Performance and accuracy of hardware-oriented native-, emulated- and m || Hydrodynamics and mass transfer in non‐Newtonian solutions in a bubble || Improving the permeate flux by unsteady operation of a RO desalination |
| 3 | bottom | Trunk muscle activation patterns during walking at different speeds. || TGFβ-mediated polarization of decidual neutrophils || Specialisation in Broca's region for semantic, phonological, and synta |
| 4 | top | Practical Approaches to Kalman Filtering with Time-Correlated Measurem || The effect of out-of-plane motion on 2D and 3D digital image correlati || Ensemble of surrogates |
| 4 | bottom | The String landscape, black holes and gravity as the weakest force || Applications of the KKM Property to Coincidence Theorems, Equilibrium  || All admissible meromorphic solutions of Hayman's equation |
| 5 | top | Impact of aortic stiffness on survival in end-stage renal disease. || Oesophageal peristalsis and acid clearance. A method for its study || Newton's Method and Secant Method for Set-Valued Mappings |
| 5 | bottom | Race, gender, and partnership in the patient-physician relationship. || Gate-Tunable WSe2/SnSe2 Backward Diode with Ultrahigh-Reverse Rectific || The research community and the private sector: a hands-on or hands-off |
| 6 | top | A tunable impedance surface performing as a reconfigurable beam steeri || Estimating Distribution of Hidden Objects with Drones: From Tennis Bal || Sharp global well-posedness for KdV and modified KdV on ℝ and |
| 6 | bottom | Rare arachnids from Malaysia and Sumatra || Catchment properties, function, and conceptual model representation: i || A system for expressing net energy requirements and feed values for gr |
| 7 | top | Axisymmetric deformations of a 2nd grade elastic cylinder || Similarity is closeness: Metaphorical mapping in a conceptual task || Fronts and bumps in spatially extended Kuramoto networks |
| 7 | bottom | Load Balanced MinMin Algorithm for Static MetaTask Scheduling in Grid  || Dynamic Adaptive Point Cloud Streaming || Hadronic top-quark pair production with NNLL threshold resummation |
| 8 | top | The nature of work family conflict: A review and agenda for future res || 3D Bioprinted Human Skeletal Muscle Constructs for Muscle Function Res || Tunneling resistance and its effect on the electrical conductivity of  |
| 8 | bottom | Seasonal and Geographic Variation of Southern Blue Whale Subspecies in || La2010: a new orbital solution for the long-term motion of the Earth || Genetic serum protein markers (HP, TF, GC and PI) in eight Slovakian p |
| 9 | top | Principles of Selective Ion Transport in Channels and Pumps || Dynamic reliability: towards an integrated platform for probabilistic  || On the stress singularities in the plane elasticity of the composite w |
| 9 | bottom | Antioxidant activity and phenolic content of selected fruit seeds || Genetic algorithms as a strategy for feature selection || Synthesis, characterization and in vitro toxicity assessment of DMPS-c |
| 10 | top | Application of model-selection criteria to some problems in multivaria || Exploration of a Novel Intermediate Response Endpoint in Immunotherapy || A statistical framework for SNP calling, mutation discovery, associati |
| 10 | bottom | Representation Theory of Artin Algebras I || The tension-free hernioplasty. || Psychological responses of elite young riders to the injury of their h |
| 11 | top | Mechanism of action of insecticidal secondary metabolites of plant ori || Chirality and natural optical activity in disordered media || The analysis of elliptic families |
| 11 | bottom | A micro-pitting model for spur gear contacts || Upper and lower bound limit analysis of plates using FEM and second-or || Hydrogen embrittlement associated with strain localization in a precip |
| 12 | top | Symmetry and density-functional exchange and correlation || An information geometric approach to supervised dimensionality reducti || Cortical Mapping of Gait in Humans: A Near-Infrared Spectroscopic Topo |
| 12 | bottom | Bubble-up: Increasing utilization in modern warehouse scale computers  || Efficient Coverability Analysis by Proof Minimization || Respiration in MA-packed, cut carrots |
| 13 | top | Building better batteries || High-temperature superconductivity in iron-based materials || Peter Schmidt: Econometrician and consummate professional |
| 13 | bottom | On Ozaki's condition for p-valency || Waves that appear from nowhere and disappear without a trace || Three-dimensional STED microscopy of aberrating tissue using dual adap |
| 14 | top | Improvement on sulfate resistance of blended cement with high alumina  || Clustering and preferential attachment in growing networks. || The impact of anthropogenic land use and land cover change on regional |
| 14 | bottom | Erosion of scientific standards: where will it end? || Drugs of abuse: behavioural principles, methods and terms. || The cucurbit[n]uril family. |
| 15 | top | Scaling limits of loop-erased random walks and uniform spanning trees || Photoluminescence Enhancement through Symmetry Breaking Induced by Def || A resource-efficient adaptive Fourier analyzer |
| 15 | bottom | Stripping foils at RHIC || In-beam study of 105Ag and configuration-dependent triaxiality in nucl || On the new fractional derivative and application to nonlinear Fisher's |
| 16 | top | The initial value problem for the equations of motion of viscous and h || Double-Barred Galaxies I. A Catalog of Barred Galaxies with Stellar Se || Solitary waves with the Madelung fluid description: A generalized deri |
| 16 | bottom | Fabrication yields of serially harvested calf-fed Holstein steers fed  || Unlearning versus savings in visuomotor adaptation: comparing effects  || How do subvocal rehearsal and general attentional resources contribute |
| 17 | top | On certain problem in the class of k-starlike functions || Ocular bacterial flora in contact lens wearers || 1/3 Tubular plating as a method of first metatarsophalangeal joint fus |
| 17 | bottom | Risk perception of mobile communication: a mental models approach || Autism and creativity. Is there a link between autism and exceptional  || Evaluation and interpretation of symptom structures in patients with s |
| 18 | top | A uniformly second order fast sweeping method for eikonal equations || Polarizable empirical force field for the primary and secondary alcoho || Using sulfur as a tracer of outdoor fine particulate matter. |
| 18 | bottom | Computing diameter constrained reliability of a network with junction  || Threshold models in restoration and conservation: a developing framewo || Degeneracy and complexity in biological systems |
| 19 | top | The curriculum from 5 to 16 || Continuous recording of photochemical and non-photochemical chlorophyl || Eco-innovations in the functioning of companies. |
| 19 | bottom | Structural identification of a bacterial quorum-sensing signal contain || Long-term neurocognitive function after critical illness. || Survey on Fall Detection and Fall Prevention Using Wearable and Extern |
| 20 | top | The Effect of Observer Perspective on the Perceived Velocity of Human  || It's All about Me: Narcissistic Chief Executive Officers and Their Eff || Freshly induced short-lived gamma-ray activity as a measure of fission |
| 20 | bottom | Pre-service student-teacher self-efficacy beliefs: An insight Into the || Reduced-order H∞ filter of singular Markovian jump systems with mode-d || Trajectories of boys' physical aggression, opposition, and hyperactivi |
| 21 | top | Electroreductive generation of active base and its application to orga || Gender and Reactions to Psychological Problems: An Examination of Soci || Entropy-Based Statistical Analysis of PolSAR Data |
| 21 | bottom | An in‐depth study of misconceptions in stoichiometry and chemical equi || Effects of dietary sodium and chloride on growth, efficiency of feed u || The Effect of Resecting a Part of the Uterus on the Formation of the H |
| 22 | top | Statistical eye model for normal eyes. || Apolipoprotein E: cholesterol transport protein with expanding role in || Nucleoside conformations. XVII. A PMR study of 2'-anhydronucleosides a |
| 22 | bottom | Local and Parallel Finite Element Algorithms Based on Two-Grid Discret || Efficient Coverability Analysis by Proof Minimization || UNIFORM PROCEDURES IN UNCOUNTABLE STRUCTURES |
| 23 | top | Small-Scale Challenges to the ΛCDM Paradigm || Kilohertz Quasi-periodic Oscillations in Neutron Star Binaries Modeled || Hanfets, a barley and wheat mixture in Eritrea: Yield, stability and f |
| 23 | bottom | The effect of out-of-plane motion on 2D and 3D digital image correlati || Workgroup Report: Drinking-Water Nitrate and Health—Recent Findings an || Decrease in Anogenital Distance among Male Infants with Prenatal Phtha |
| 24 | top | Ocular bacterial flora in contact lens wearers || Language Contact and New Dialect Formation: Evidence from German in No || An in‐depth study of misconceptions in stoichiometry and chemical equi |
| 24 | bottom | Local and Parallel Finite Element Algorithms Based on Two-Grid Discret || The Cynical Genius Illusion: Exploring and Debunking Lay Beliefs About || Frequency comparison of two high-accuracy Al+ optical clocks. |
| 25 | top | Quantized hall effect || All admissible meromorphic solutions of Hayman's equation || Pfam: the protein families database |
| 25 | bottom | Phase Matching For Large-scale Frequency Upconversion in Plasma. || Utilization of byproducts and waste materials from meat, poultry and f || Effect of pH and calcium level on the biochemical, textural and functi |
| 26 | top | Load Balanced MinMin Algorithm for Static MetaTask Scheduling in Grid  || Pain Processing in Four Regions of Human Cingulate Cortex Localized wi || How Many Psychiatrists Do We Need? |
| 26 | bottom | Generalized approximate message passing for estimation with random lin || Emotional regulation and display in classroom victims of bullying: Cha || Reducing the peak-to-average power ratio in OFDM by cyclically shiftin |
| 27 | top | Modal verbs in Catalan || Peter Schmidt: Econometrician and consummate professional || Local and Parallel Finite Element Algorithms Based on Two-Grid Discret |
| 27 | bottom | Update semantics of relational views || Management of disruptive behaviour within nursing work environments: a || SDF^3: SDF For Free |
| 28 | top | Medium-spin structure of 96,97Sr and 98,99Zr nuclei and the onset of d || Outdoor MIMO wireless channels: models and performance prediction || Fabrication yields of serially harvested calf-fed Holstein steers fed  |
| 28 | bottom | Efficient Design for Mendelian Randomization Studies: Subsample and 2- || On the need to rewrite the history of Greek mathematics || Alterations in the uterine microbiome in patients with early endometri |
| 29 | top | Pre-service student-teacher self-efficacy beliefs: An insight Into the || Research, Perspectives, and Recommendations on Implementing the Flippe || The effect of streptozotocin-induced diabetes on cell proliferation in |
| 29 | bottom | Unified treatment of quantum coherent and incoherent hopping dynamics  || Effect of pH and calcium level on the biochemical, textural and functi || Continuous Newton's Method for Power Flow Analysis |
| 30 | top | Local and Parallel Finite Element Algorithms Based on Two-Grid Discret || The String landscape, black holes and gravity as the weakest force || Valuing health‐related quality of life: An EQ‐5D‐5L value set for Engl |
| 30 | bottom | Metal-Poor Stars and the Chemical Enrichment of the Universe || Self-similar evolution of parabolic pulses in a laser. || Research on resilience and its implications for tobacco prevention. |
