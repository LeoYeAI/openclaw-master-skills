import { SecurityPattern, Severity } from '../../types';

export const serializationPatterns: SecurityPattern[] = [
  {
    id: 'serialization_001',
    category: 'serialization',
    subcategory: 'java_serialized_base64',
    pattern: /rO0AB[A-Za-z0-9+/=]{10,}/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Java serialized object (base64-encoded magic bytes)',
    examples: [
      'rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcA=='
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['serialization', 'java', 'base64', 'critical']
  },
  {
    id: 'serialization_002',
    category: 'serialization',
    subcategory: 'java_serialized_hex',
    pattern: /aced0005[0-9a-f]{8,}/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Java serialized object (hex-encoded magic bytes)',
    examples: [
      'aced00057372001164656d6f2e4d61696e436c617373'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['serialization', 'java', 'hex', 'critical']
  },
  {
    id: 'serialization_003',
    category: 'serialization',
    subcategory: 'java_objectinputstream',
    pattern: /(?:ObjectInputStream|readObject|readUnshared)\s*\(/i,
    severity: Severity.HIGH,
    language: 'all',
    description: 'Java ObjectInputStream deserialization',
    examples: [
      'new ObjectInputStream(input).readObject()',
      'ois.readObject()',
      'stream.readUnshared()'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['serialization', 'java', 'objectinputstream']
  },
  {
    id: 'serialization_004',
    category: 'serialization',
    subcategory: 'php_serialized_object',
    pattern: /O:\d+:"[^"]+"/,
    severity: Severity.HIGH,
    language: 'all',
    description: 'PHP serialized object notation',
    examples: [
      'O:8:"stdClass":1:{s:4:"name";s:4:"test";}',
      'O:14:"SplFileObject":0:{}'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['serialization', 'php', 'object']
  },
  {
    id: 'serialization_005',
    category: 'serialization',
    subcategory: 'php_unserialize',
    pattern: /\bunserialize\s*\(/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'PHP unserialize() function call',
    examples: [
      'unserialize($user_input)',
      'unserialize(base64_decode($data))'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['serialization', 'php', 'unserialize', 'critical']
  },
  {
    id: 'serialization_006',
    category: 'serialization',
    subcategory: 'python_pickle_magic',
    pattern: /(?:\\x80\\x0[345]|gASV|\\x80\\x05)/,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Python pickle serialized object magic bytes',
    examples: [
      '\\x80\\x03cposix\\nsystem\\n',
      'gASVKAAAAA==',
      '\\x80\\x05\\x95'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['serialization', 'python', 'pickle', 'critical']
  },
  {
    id: 'serialization_007',
    category: 'serialization',
    subcategory: 'python_pickle_loads',
    pattern: /pickle\.(?:loads?|Unpickler)\s*\(/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Python pickle.loads()/Unpickler deserialization',
    examples: [
      'pickle.loads(user_data)',
      'pickle.load(file_obj)',
      'pickle.Unpickler(data).load()'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['serialization', 'python', 'pickle', 'critical']
  },
  {
    id: 'serialization_008',
    category: 'serialization',
    subcategory: 'yaml_unsafe_tags',
    pattern: /!!(?:python\/object|ruby\/object|java\/object|binary|map|seq)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'YAML unsafe deserialization tags',
    examples: [
      '!!python/object/apply:os.system ["id"]',
      '!!ruby/object:Gem::Installer',
      '!!python/object/new:subprocess.check_output [["ls"]]'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['serialization', 'yaml', 'unsafe-tag', 'critical']
  },
  {
    id: 'serialization_009',
    category: 'serialization',
    subcategory: 'dotnet_binaryformatter',
    pattern: /(?:BinaryFormatter|SoapFormatter|LosFormatter|ObjectStateFormatter)\s*(?:\(|\.)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: '.NET BinaryFormatter/SoapFormatter unsafe deserialization',
    examples: [
      'new BinaryFormatter().Deserialize(stream)',
      'new SoapFormatter().Deserialize(input)',
      'new LosFormatter().Deserialize(data)'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['serialization', 'dotnet', 'binaryformatter', 'critical']
  },
  {
    id: 'serialization_010',
    category: 'serialization',
    subcategory: 'dotnet_typenamehandling',
    pattern: /TypeNameHandling\s*[=:]\s*(?:TypeNameHandling\.)?(?:All|Auto|Objects|Arrays)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: '.NET JSON TypeNameHandling unsafe configuration',
    examples: [
      'TypeNameHandling = TypeNameHandling.All',
      '"TypeNameHandling": "Auto"',
      'TypeNameHandling: Objects'
    ],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: ['serialization', 'dotnet', 'json', 'typenamehandling', 'critical']
  },
  {
    id: 'serialization_011',
    category: 'serialization',
    subcategory: 'dotnet_viewstate',
    pattern: /__VIEWSTATE[^=]*=\s*[A-Za-z0-9+/=]{50,}/i,
    severity: Severity.HIGH,
    language: 'all',
    description: '.NET ViewState potentially containing serialized payload',
    examples: [
      '__VIEWSTATE=/wEPDwUKLTEyNTc0MDM...(long base64)...'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['serialization', 'dotnet', 'viewstate']
  },
  {
    id: 'serialization_012',
    category: 'serialization',
    subcategory: 'java_gadget_chains',
    pattern: /(?:org\.apache\.commons\.collections|org\.apache\.xalan|com\.sun\.org\.apache\.xalan|org\.codehaus\.groovy\.runtime|org\.springframework\.beans\.factory)/i,
    severity: Severity.CRITICAL,
    language: 'all',
    description: 'Java deserialization gadget chain class references',
    examples: [
      'org.apache.commons.collections.functors.InvokerTransformer',
      'org.apache.xalan.xsltc.trax.TemplatesImpl',
      'org.springframework.beans.factory.ObjectFactory'
    ],
    falsePositiveRisk: 'medium',
    enabled: true,
    tags: ['serialization', 'java', 'gadget-chain', 'critical']
  }
];
