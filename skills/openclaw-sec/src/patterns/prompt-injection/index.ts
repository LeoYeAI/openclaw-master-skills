import { instructionOverridePatterns } from './instruction-override';
import { roleManipulationPatterns } from './role-manipulation';
import { systemImpersonationPatterns } from './system-impersonation';
import { jailbreakPatterns } from './jailbreak-attempts';
import { directExtractionPatterns } from './direct-extraction';
import { socialEngineeringPatterns } from './social-engineering';
import { cotHijackingPatterns } from './cot-hijacking';
import { policyPuppetryPatterns } from './policy-puppetry';
import { extractionAttackPatterns } from './extraction-attacks';
import { encodingObfuscationPatterns } from './encoding-obfuscation';

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
