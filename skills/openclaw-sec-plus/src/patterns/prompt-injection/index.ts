import { instructionOverridePatterns } from './instruction-override';
import { instructionOverridePatternsZH } from './instruction-override-zh';
import { roleManipulationPatterns } from './role-manipulation';
import { roleManipulationPatternsZH } from './role-manipulation-zh';
import { systemImpersonationPatterns } from './system-impersonation';
import { systemImpersonationPatternsZH } from './system-impersonation-zh';
import { jailbreakPatterns } from './jailbreak-attempts';
import { jailbreakPatternsZH } from './jailbreak-attempts-zh';
import { directExtractionPatterns } from './direct-extraction';
import { directExtractionPatternsZH } from './direct-extraction-zh';
import { socialEngineeringPatterns } from './social-engineering';
import { socialEngineeringPatternsZH } from './social-engineering-zh';
import { cotHijackingPatterns } from './cot-hijacking';
import { cotHijackingPatternsZH } from './cot-hijacking-zh';
import { policyPuppetryPatterns } from './policy-puppetry';
import { policyPuppetryPatternsZH } from './policy-puppetry-zh';
import { extractionAttackPatterns } from './extraction-attacks';
import { extractionAttackPatternsZH } from './extraction-attacks-zh';
import { encodingObfuscationPatterns } from './encoding-obfuscation';
import { encodingObfuscationPatternsZH } from './encoding-obfuscation-zh';

export const promptInjectionPatternsEN = [
  ...instructionOverridePatterns,
  ...roleManipulationPatterns,
  ...systemImpersonationPatterns,
  ...jailbreakPatterns,
  ...directExtractionPatterns,
  ...socialEngineeringPatterns,
  ...cotHijackingPatterns,
  ...policyPuppetryPatterns,
  ...extractionAttackPatterns,
  ...encodingObfuscationPatterns
];

export const promptInjectionPatternsZH = [
  ...instructionOverridePatternsZH,
  ...roleManipulationPatternsZH,
  ...systemImpersonationPatternsZH,
  ...jailbreakPatternsZH,
  ...directExtractionPatternsZH,
  ...socialEngineeringPatternsZH,
  ...cotHijackingPatternsZH,
  ...policyPuppetryPatternsZH,
  ...extractionAttackPatternsZH,
  ...encodingObfuscationPatternsZH
];
