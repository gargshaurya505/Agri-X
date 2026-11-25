export const TOMATO_DISEASES = [
  {
    id: 0,
    slug: 'bacterial_spot',
    name: 'Bacterial Spot',
    scientific_name: 'Xanthomonas campestris pv. vesicatoria',
    category: 'Bacterial Disease',
    severity: 'High',
    description: 'Bacterial spot is a devastating foliar and fruit disease that flourishes in warm, humid climates, frequently causing premature leaf drop and unmarketable blemished tomatoes.',
    symptoms: [
      'Small, water-soaked, dark brown circular lesions on leaves (often < 3mm).',
      'Lesions develop a distinctive yellow halo as they enlarge.',
      'Centers of lesions frequently tear and dry out, leaving shot-hole perforations.',
      'Raised, scabby spots on green and ripe tomato fruit.'
    ],
    prevention: [
      'Use certified disease-free seeds and transplants.',
      'Avoid overhead sprinkler irrigation; apply water via drip irrigation directly at the root zone.',
      'Implement strict 2-3 year crop rotations away from solanaceous plants.'
    ],
    management: [
      'Apply preventive copper-based bactericides combined with mancozeb during rainy, humid vegetative windows.',
      'Prune and destroy infected plant foliage promptly outside the field.',
      'Sanitize tools, stakes, and footwear with dilute quaternary ammonium or bleach solutions.'
    ]
  },
  {
    id: 1,
    slug: 'early_blight',
    name: 'Early Blight',
    scientific_name: 'Alternaria solani',
    category: 'Fungal Disease',
    severity: 'Moderate to High',
    description: 'A common fungal infection of tomato foliage that initiates on older bottom leaves and progressively climbs up the canopy, causing severe defoliation and sunscald.',
    symptoms: [
      'Characteristic concentric dark brown or black rings creating a "target-board" pattern.',
      'Surrounding leaf tissue turns yellow and eventually withers entirely.',
      'Sunken, dark leathery cankers on stems and fruit near the stem calyx.'
    ],
    prevention: [
      'Maintain wide crop spacing to promote rapid leaf drying through adequate airflow.',
      'Apply organic or plastic mulch around the plant base to prevent soil-splashing.',
      'Destroy or deep-till crop residues immediately after harvest.'
    ],
    management: [
      'Apply protective fungicides (chlorothalonil, azoxystrobin, or copper hydroxide) at the first sighting.',
      'Prune lower leaves up to 12-18 inches from the ground to prevent soil spore contamination.',
      'Stake or trellis vines to keep foliage upright and dry.'
    ]
  },
  {
    id: 2,
    slug: 'late_blight',
    name: 'Late Blight',
    scientific_name: 'Phytophthora infestans',
    category: 'Oomycete / Water Mold',
    severity: 'Critical / Extreme',
    description: 'The infamous pathogen responsible for the Irish potato famine. Late blight spreads with extreme velocity under cool, wet conditions, capable of destroying entire crops in days.',
    symptoms: [
      'Large, irregular, pale water-soaked lesions that rapidly expand and turn purplish-brown.',
      'Delicate white fungal mycelium visible on the undersides of leaves during high humidity.',
      'Dark brown, greasy lesions expanding across green and ripening fruit.'
    ],
    prevention: [
      'Plant resistant varieties whenever available.',
      'Eliminate volunteer tomato and potato plants from surrounding borders.',
      'Scout daily during prolonged cool, cloudy, damp weather periods (60-70°F).'
    ],
    management: [
      'Apply systemic preventative fungicides (e.g., cymoxanil, mandipropamid) prior to rain events.',
      'Immediately remove and bag heavily infected plants; do not compost them.',
      'Inform neighboring growers when late blight is confirmed in the area.'
    ]
  },
  {
    id: 3,
    slug: 'leaf_mold',
    name: 'Leaf Mold',
    scientific_name: 'Passalora fulva',
    category: 'Fungal Disease',
    severity: 'Moderate',
    description: 'Primarily a greenhouse and high-tunnel pathology where high humidity (>85%) and poor air movement allow olive-green fungal sporulation on leaf undersides.',
    symptoms: [
      'Pale green or yellowish chlorotic patches on the upper leaf surface with indistinct margins.',
      'Dense, velvety, olive-green to brown fungal growth directly beneath the yellow patches on the underside.',
      'In severe cases, leaves curl, wither, and drop prematurely.'
    ],
    prevention: [
      'Increase ventilation in greenhouses and tunnels using exhaust fans and vents.',
      'Maintain humidity below 85% through heating and air circulation.',
      'Use drip irrigation to prevent leaves from remaining wet.'
    ],
    management: [
      'Prune dense canopy foliage to enhance light penetration and air movement.',
      'Apply biofungicides (Bacillus subtilis) or targeted copper fungicides upon early detection.'
    ]
  },
  {
    id: 4,
    slug: 'septoria_leaf_spot',
    name: 'Septoria Leaf Spot',
    scientific_name: 'Septoria lycopersici',
    category: 'Fungal Disease',
    severity: 'Moderate to High',
    description: 'A destructive fungal leaf spot pathogen that attacks leaves, petioles, and stems, leading to severe defoliation and loss of photosynthetic capacity.',
    symptoms: [
      'Numerous small (1-3mm), circular spots with dark brown margins and sunken grayish-white centers.',
      'Tiny, pepper-like black specks (pycnidia fungal fruiting bodies) inside the light centers.',
      'Heavily spotted leaves turn completely yellow and wither.'
    ],
    prevention: [
      'Enforce crop rotations of at least 3 years away from nightshades.',
      'Control weed hosts such as horsenettle and nightshade near fields.',
      'Thoroughly clean up and discard old crop debris at the conclusion of the season.'
    ],
    management: [
      'Begin protective fungicide applications (chlorothalonil or mancozeb) when bottom foliage shows symptoms.',
      'Never prune or handle plants when wet with dew or irrigation.'
    ]
  },
  {
    id: 5,
    slug: 'spider_mites',
    name: 'Spider Mites',
    scientific_name: 'Tetranychus urticae',
    category: 'Arachnid Pest',
    severity: 'Moderate',
    description: 'Microscopic arachnids (Two-Spotted Spider Mites) that colonize leaf undersides, puncturing plant cells with piercing-sucking mouthparts to feed on plant sap.',
    symptoms: [
      'Fine white, yellow, or bronze stippling / speckling across the upper leaf surface.',
      'Silken webbing visible across branch crotches and leaf undersides under heavy infestations.',
      'Leaves take on a dull, bronzed appearance and dry out.'
    ],
    prevention: [
      'Avoid dusty conditions near roadways, as dust suppresses beneficial predatory insects.',
      'Conserve natural predators such as lady beetles, lacewings, and predatory mites.',
      'Monitor plants weekly during hot, dry summer weather.'
    ],
    management: [
      'Spray plant undersides thoroughly with insecticidal soaps or horticultural oils.',
      'Introduce commercially reared predatory mites (Phytoseiulus persimilis).',
      'Rotate miticides with different modes of action to prevent rapid resistance buildup.'
    ]
  },
  {
    id: 6,
    slug: 'target_spot',
    name: 'Target Spot',
    scientific_name: 'Corynespora cassiicola',
    category: 'Fungal Disease',
    severity: 'Moderate',
    description: 'A fungal foliar and fruit pathogen common in warm, humid agricultural zones that produces dark brown target-like concentric rings on leaves and fruit.',
    symptoms: [
      'Small, pinpoint brown spots that expand to circular or irregular brown lesions.',
      'Faint concentric zones within the lesion, often with light brown centers and chlorotic halos.',
      'Cracked, sunken brown lesions on tomato fruit.'
    ],
    prevention: [
      'Ensure wide row spacing to facilitate air drainage and sun exposure.',
      'Avoid overhead watering schedules.',
      'Implement good field sanitation by clearing old solanaceous remnants.'
    ],
    management: [
      'Apply fungicides labeled for target spot (e.g., azoxystrobin, chlorothalonil, or pyraclostrobin).',
      'Remove lower diseased foliage to impede vertical canopy spread.'
    ]
  },
  {
    id: 7,
    slug: 'yellow_leaf_curl_virus',
    name: 'Tomato Yellow Leaf Curl Virus',
    scientific_name: 'Tomato yellow leaf curl virus (TYLCV)',
    category: 'Viral Disease',
    severity: 'High to Extreme',
    description: 'A begomovirus transmitted exclusively by the sweetpotato whitefly (Bemisia tabaci). Infected young plants are severely stunted and typically set little to no fruit.',
    symptoms: [
      'Upward curling and cupping of leaflet margins.',
      'Marked interveinal yellowing (chlorosis) on new terminal shoots.',
      'Severe plant stunting with compacted, bushy growth habits.',
      'Flowers drop before pollination, resulting in drastic yield collapse.'
    ],
    prevention: [
      'Plant TYLCV-resistant or tolerant tomato hybrids.',
      'Install fine insect-proof mesh netting (50+ mesh) in nursery and seedling zones.',
      'Use reflective silver mulches to repel vectoring whiteflies.'
    ],
    management: [
      'Manage whitefly populations using systemic insecticides or insecticidal soaps.',
      'Immediately rogue out and destroy symptomatic infected plants in sealed plastic bags.',
      'Eradicate host weeds surrounding field perimeters.'
    ]
  },
  {
    id: 8,
    slug: 'mosaic_virus',
    name: 'Tomato Mosaic Virus',
    scientific_name: 'Tomato mosaic virus (ToMV)',
    category: 'Viral Disease',
    severity: 'Moderate to High',
    description: 'A remarkably stable tobamovirus that is spread mechanically through contaminated hands, tools, pruning shears, and contact between overlapping plants.',
    symptoms: [
      'Mottled light and dark green mosaic patterns across leaf lamina.',
      'Distorted, narrow, or "shoestring-like" leaf blades (fern-leafing).',
      'Brown internal browning (blotchy ripening) inside harvested fruit.'
    ],
    prevention: [
      'Wash hands thoroughly with soap or 20% nonfat dry milk solution before working with plants.',
      'Prohibit tobacco smoking or handling near tomato facilities, as tobacco products harbor viruses.',
      'Disinfect all pruning shears and tools regularly in a 10% trisodium phosphate (TSP) solution.'
    ],
    management: [
      'There is no chemical cure for viral infections once established inside vascular tissue.',
      'Rogue out and destroy infected vines immediately to prevent mechanical transmission.',
      'Select seed lots certified free of tobamoviruses.'
    ]
  },
  {
    id: 9,
    slug: 'healthy',
    name: 'Healthy Leaf',
    scientific_name: 'Solanum lycopersicum',
    category: 'Healthy',
    severity: 'None',
    description: 'Normal, vigorous tomato leaf tissue displaying intact cellular structure, vibrant green pigmentation, robust photosynthetic output, and no visible lesion indicators.',
    symptoms: [
      'Uniform deep green coloration across upper and lower surfaces.',
      'Smooth leaflet edges without curling, cupping, or chlorotic halos.',
      'Absence of fungal mycelia, necrotic spots, or insect webbing.'
    ],
    prevention: [
      'Maintain balanced nitrogen, phosphorus, and potassium soil fertility.',
      'Provide consistent watering to prevent blossom end rot and physiological stress.',
      'Continue regular scouting routines to detect early signs of pest or pathogen pressure.'
    ],
    management: [
      'Continue current cultural and agronomic care practices.',
      'Maintain clean growing zones and adequate sunlight exposure.'
    ]
  }
];
