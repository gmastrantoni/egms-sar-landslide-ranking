# EGMS SAR Landslide Ranking
This repository contains a workflow for the automatic ranking of landslide candidate areas at a regional scale using EGMS InSAR data for territorial planning and risk management.

A semi-automated methodology for identifying and ranking landslide candidate areas at regional scale using European Ground Motion Service (EGMS) InSAR data for territorial planning and risk management.

## Overview

This repository contains Python scripts implementing the methodology described in the research paper for automatic ranking of landslide candidate areas using EGMS InSAR data. The approach transforms large-scale interferometric data into actionable insights for regional authorities responsible for landslide risk mitigation and territorial planning.

## Key Features

- **Automated AOI Detection**: Semi-automatic identification of Areas of Interest (AOIs) based on velocity anomalies from A-DInSAR analysis
- **Multi-criteria Ranking System**: Hazard and risk-oriented ranking combining intensity metrics and exposure factors
- **Regional Scale Analysis**: Capable of processing extensive areas with thousands of measurement points
- **Integration Ready**: Compatible with existing landslide inventories (IFFI, PAI) and infrastructure databases

## Methodology

The implemented workflow consists of three main components:

1. **Selection of Landslide Candidates**: Identification of AOIs based on Persistent Scatterer distribution from A-DInSAR analysis
2. **Intensity and Exposure Ranking**: Hierarchical classification evaluating both hazard-oriented (velocity, area) and risk-oriented (buildings, infrastructure) criteria
3. **Validation Framework**: Ground-truth validation through field surveys and geomorphological analysis

## Input Data Requirements

- **EGMS Basic Products**: Sentinel-1 time series and LOS velocity maps (ascending/descending)
- **Digital Elevation Model**: High-resolution DEM (10m resolution recommended)
- **Landslide Inventories**: IFFI Project maps or PAI Hazard Maps
- **Infrastructure Data**: Vector maps of roads, railways, and urbanized areas
- **Anthropogenic Features**: Quarries, mines, landfills, and industrial plants

## Case Study

The methodology was validated on the Lazio Region (Central Italy), identifying 4,811 unique Areas of Interest with 91% field validation success rate. The analysis revealed significant gaps in existing landslide inventories, with 68% of identified active areas not previously mapped.

## Technical Specifications

- **Velocity Threshold**: ±2.5 mm/year for anomaly detection
- **Interpolation Method**: Inverse Distance Weighting (IDW) with 50m radius
- **Minimum PS Requirements**: 6 persistent scatterers within interpolation radius
- **Clustering Distance**: Maximum 200m between related deformation areas
- **Slope Filtering**: Areas with >5° slope inclination

## Citation

If you use this methodology or code in your research, please cite:

```bibtex
@article{marmoni2024automatic,
  title={Automatic ranking of landslide candidate areas at a regional scale using EGMS InSAR data for territorial planning and risk management},
  author={Marmoni, Gian Marco and Antonielli, Benedetta and Caprari, Patrizia and Di Renzo, Maria Elena and Marini, Roberta and Mastrantoni, Giandomenico and Mazzanti, Paolo and Patelli, Davide and Bozzano, Francesca},
  journal={[Journal Name]},
  year={2024},
  note={Corresponding author: gianmarco.marmoni@uniroma1.it}
}
```

## Authors

**Corresponding Author:**
- Gian Marco Marmoni (gianmarco.marmoni@uniroma1.it)

**Contributors:**
- Benedetta Antonielli¹
- Patrizia Caprari¹
- Maria Elena Di Renzo¹
- Roberta Marini²
- Giandomenico Mastrantoni¹
- Paolo Mazzanti¹,²
- Davide Patelli¹
- Francesca Bozzano¹

**Affiliations:**
1. Earth Science Department of Sapienza University of Rome and CERI Research Centre for Geological Risks, P.le Aldo Moro 5, Rome, Italy
2. NHAZCA S.r.l., Via Vittorio Bachelet, Rome, Italy

## Acknowledgments

This study was conducted within the framework of:
- Institutional agreement between CERI Research Centre for Geological Risks and Lazio Region
- RETURN Extended Partnership (European Union Next-GenerationEU, NRRP Mission 4, Component 2, Investment 1.3)
- ReLUIS 2022-2024 & 2024-2026 Projects

COSMO-SkyMed Product ©ASI - (2022) processed by CERI under license of the Italian Space Agency (ASI).

## Keywords

EGMS, Automatic selection, landslide candidates, intensity ranking, interferometry, landslide risk, A-DInSAR, territorial planning, risk management

## License

[Add appropriate license information]

## Contributing

[Add contribution guidelines if applicable]

## Support

For questions or issues, please contact the corresponding author or open an issue in this repository.