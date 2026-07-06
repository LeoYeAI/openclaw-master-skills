---
name: prompt-generator
description: Generate high-quality, customizable AI prompts for various use cases including creative writing, problem-solving, education, business, programming, Flutter development, and game development. Use when a user asks for help creating prompts, wants to improve their AI interactions, or needs structured prompt templates for specific tasks.
---

# AI Prompt Generator

## Overview

Generate high-quality, customizable AI prompts that help users get better results from AI tools. This skill provides structured templates, best practices, and prompt generation for various use cases including Flutter app development and game development.

## Core Features

- **Multiple Prompt Categories**: Creative, Problem-Solving, Educational, Business, Programming, Flutter Development, Game Development
- **Tone & Style Customization**: Formal, Casual, Technical, Creative, Professional
- **Length & Complexity Control**: Short, Medium, Detailed | Beginner, Intermediate, Advanced
- **Context Enhancement**: Add background, constraints, and specific requirements
- **Template Library**: Pre-built templates with customization options
- **Real-time Guidance**: Best practices and tips for effective prompts

## Usage

### Basic Usage

1. **Select Prompt Type**: Choose from available categories
2. **Define Your Goal**: What do you want the AI to help with?
3. **Customize**: Adjust tone, length, complexity
4. **Add Context**: Include relevant background information
5. **Generate**: Get your structured prompt
6. **Use**: Copy and paste into your AI tool

### Advanced Usage

1. **Template System**: Save and load custom templates
2. **Iterative Refinement**: Improve prompts based on results
3. **Multi-step Prompts**: Create complex, multi-stage prompts
4. **Constraint Addition**: Add specific requirements and limitations
5. **Output Formatting**: Define how you want the response structured

## Prompt Categories

### 1. Creative Writing Prompts

**Structure:**
```
Role: [creative writer/editor]
Task: [specific writing task]
Context: [background, setting, characters]
Constraints: [word count, style, tone]
Output: [expected format]
```

**Example:**
```
You are a creative fiction writer. Write a detailed short story about an astronaut's 
experience on a solo mission. Include emotional challenges, a turning point in the 
plot, and a meaningful ending. Target length: 1500 words. Tone: Reflective and 
introspective.
```

### 2. Problem-Solving Prompts

**Structure:**
```
Context: [situation/background]
Problem: [specific issue]
Constraints: [limitations, requirements]
Desired Output: [solution format]
Success Criteria: [how to measure success]
```

**Example:**
```
I'm experiencing [specific technical issue] in [context/environment]. The problem 
occurs when [specific conditions]. I've tried [previous attempts]. Constraints: 
[cannot change X, must work with Y]. Provide step-by-step troubleshooting with 
explanations for each step.
```

### 3. Educational Prompts

**Structure:**
```
Topic: [subject matter]
Audience: [who is learning]
Learning Objective: [what they should understand]
Teaching Method: [explanation style]
Assessment: [how to verify understanding]
```

**Example:**
```
Explain [complex concept] to [beginners/intermediate/advanced learners] using 
[analogies/examples/step-by-step approach]. Include practical examples and 
address common misconceptions. Provide a brief quiz at the end to check 
understanding.
```

### 4. Flutter App Development Prompts

**Structure:**
```
App Type: [what kind of app]
Features: [required functionality]
State Management: [Provider/Riverpod/Bloc/etc.]
Architecture: [MVVM/Clean Architecture/etc.]
Platforms: [iOS/Android/Web/Desktop]
```

**Templates:**

#### App Architecture Setup
```
Create a Flutter app architecture for [app type] with the following requirements:
- State Management: [Provider/Riverpod/Bloc/GetX]
- Architecture Pattern: [MVVM/Clean Architecture/MVC]
- Key Features: [list main features]
- Target Platforms: [iOS/Android/Web/Desktop]
- Data Persistence: [Hive/SharedPreferences/SQLite/Firebase]
- API Integration: [REST/GraphQL/Firebase]

Provide:
1. Folder structure
2. Key files and their responsibilities
3. Dependency injection setup
4. Navigation approach
5. Error handling strategy
```

#### Feature Implementation
```
Implement [specific feature] in Flutter with these requirements:
- Feature Description: [detailed description]
- UI/UX Requirements: [design specifications]
- State Management: [how state will be managed]
- Data Flow: [how data moves through the app]
- Error Handling: [how errors are handled]
- Testing: [unit/widget/integration tests needed]

Include:
1. Complete code implementation
2. State management setup
3. UI components
4. Business logic
5. Error handling
6. Example usage
```

#### Widget Creation
```
Create a custom Flutter widget for [purpose] with these specifications:
- Widget Type: [stateless/stateful]
- Props/Parameters: [required and optional parameters]
- Styling: [theming and customization options]
- Accessibility: [semantic labels, screen reader support]
- Performance: [optimization considerations]

Provide:
1. Widget code with documentation
2. Example usage
3. Customization options
4. Performance optimizations
5. Accessibility features
```

#### State Management Setup
```
Set up state management for [app feature] using [Provider/Riverpod/Bloc]:

Requirements:
- State Type: [simple/complex/nested]
- Updates: [how state changes]
- Persistence: [local storage needs]
- Performance: [optimization requirements]

Include:
1. State model/class definition
2. State management setup
3. Provider/Bloc/Cubit implementation
4. Consumer widget examples
5. Testing approach
```

#### API Integration
```
Integrate [API name] into Flutter app with these requirements:
- API Type: [REST/GraphQL/Firebase]
- Endpoints: [list required endpoints]
- Authentication: [method]
- Error Handling: [strategy]
- Caching: [requirements]
- Offline Support: [needs]

Provide:
1. API client setup
2. Model classes
3. Repository pattern implementation
4. Error handling
5. Caching strategy
6. Example usage
```

### 5. Flutter Game Development Prompts

**Structure:**
```
Game Type: [2D/2.5D/puzzle/platformer/etc.]
Engine: [Flame/Forge2D/custom]
Core Mechanics: [main gameplay elements]
Art Style: [visual approach]
Platforms: [mobile/web/desktop]
```

**Templates:**

#### Game Architecture Setup
```
Design a Flutter game architecture for [game type] using [Flame/Forge2D]:

Requirements:
- Game Type: [puzzle/platformer/RPG/etc.]
- Core Mechanics: [list main gameplay elements]
- Save System: [progress saving needs]
- Monetization: [ads/IAP/premium]
- Platforms: [mobile/web/desktop]

Include:
1. Game loop structure
2. Scene/screen management
3. Component system
4. State management
5. Asset management
6. Save/load system
7. Performance optimizations
```

#### Game Mechanic Implementation
```
Implement [specific game mechanic] in Flutter using [Flame/Forge2D]:

Mechanic Details:
- Type: [movement/collision/scoring/etc.]
- Player Interaction: [input methods]
- Visual Feedback: [animations/effects]
- Audio: [sound effects/music]

Provide:
1. Core mechanic code
2. Component setup
3. Collision detection (if needed)
4. Animation system
5. Input handling
6. Example usage
7. Testing approach
```

#### Character/Entity System
```
Create a character/entity system for [game type] with:

Requirements:
- Entity Types: [player/enemies/NPCs/objects]
- Behaviors: [AI/movement/interaction]
- Attributes: [health/score/abilities]
- Rendering: [sprites/animations]

Include:
1. Base entity class
2. Component system
3. Behavior trees/state machines
4. Animation system
5. Collision system
6. Example entities
7. Performance optimizations
```

#### Level/World Design
```
Design a level/world system for [game type]:

Requirements:
- Level Structure: [linear/open-world/procedural]
- Progression: [difficulty scaling/unlocks]
- Save Points: [checkpoints/persistence]
- Assets: [tilemaps/3D models/etc.]

Provide:
1. Level data structure
2. Level loading system
3. Procedural generation (if applicable)
4. Progression system
5. Asset management
6. Example levels
7. Testing approach
```

#### Game UI/UX
```
Design game UI/UX for [game type] with these screens:

Screens Needed:
- Main Menu: [options/features]
- HUD: [score/health/controls]
- Pause Menu: [options/controls]
- Game Over: [stats/restart/quit]

Include:
1. UI component structure
2. State management for UI
3. Animation/transitions
4. Responsive design
5. Accessibility features
6. Example implementations
```

#### Performance Optimization
```
Optimize Flutter game performance for [platform]:

Current Issues:
- [specific performance problems]
- [bottlenecks identified]

Target Performance:
- Frame Rate: [target FPS]
- Memory: [memory budget]
- Load Times: [acceptable load times]

Provide:
1. Profiling approach
2. Optimization strategies
3. Code improvements
4. Asset optimization
5. Memory management
6. Testing methodology
```

### 6. Business & Marketing Prompts

**Templates:**

#### Marketing Campaign
```
Create a marketing campaign for [product/service] targeting [audience]:

Campaign Goals: [awareness/conversion/engagement]
Target Audience: [demographics, interests]
Key Messages: [unique value propositions]
Channels: [social media/email/ads]
Budget: [constraints]
Timeline: [duration]

Include:
1. Campaign strategy
2. Content calendar
3. Messaging framework
4. Channel strategy
5. KPIs and measurement
6. Example content pieces
```

#### Business Strategy
```
Develop a business strategy for [company/product]:

Current Situation: [market position, challenges]
Goals: [short-term and long-term objectives]
Resources: [available assets and constraints]
Market: [industry trends, competition]

Provide:
1. Strategic analysis
2. Competitive positioning
3. Growth strategy
4. Implementation roadmap
5. Risk mitigation
6. Success metrics
```

## Best Practices

### 1. Start Clear
- Define your exact goal
- Identify your audience
- Specify desired output format
- Include relevant context

### 2. Be Specific
- Use concrete examples
- Define technical terms
- Specify scope and depth
- Include constraints

### 3. Add Context
- Provide background information
- Include relevant constraints
- Mention preferred style/approach
- Define success criteria

### 4. Iterate
- Test generated prompts
- Refine based on results
- Save successful versions
- Build on what works

### 5. Quality Check
- Review for clarity
- Ensure completeness
- Verify alignment with goals
- Check for ambiguity

## Prompt Enhancement Framework

### Context Enhancement
```
[Base Prompt]
Context: [Background information]
Constraints: [Limitations and requirements]
Examples: [Sample inputs/outputs]
Format: [Desired output structure]
```

### Constraint Addition
```
[Base Prompt]
Requirements:
- Must include [specific elements]
- Must avoid [specific elements]
- Must be [length/format]
- Must consider [specific aspects]
```

### Output Formatting
```
[Base Prompt]
Output Format:
- Structure: [paragraph/list/table/etc.]
- Length: [word count/sections]
- Style: [tone/voice]
- Include: [specific sections/elements]
```

## Common Prompt Patterns

### Role-Based Prompts
```
You are a [specific role] with expertise in [domain]. 
[Task description] considering [specific context].
Provide [output format] that includes [specific elements].
```

### Step-by-Step Prompts
```
[Task description]. Break this down into:
1. [First step]
2. [Second step]
3. [Third step]
For each step, provide [specific details].
```

### Example-Driven Prompts
```
[Task description]. Follow this pattern:
Example 1: [input] → [output]
Example 2: [input] → [output]
Now apply this to: [new input]
```

### Comparison Prompts
```
Compare [Option A] and [Option B] for [specific use case].
Consider: [criteria 1], [criteria 2], [criteria 3].
Provide recommendation with justification.
```

## Prompt Refinement Techniques

### Iterative Refinement
1. Start with basic prompt
2. Test with AI tool
3. Identify gaps/issues
4. Add missing context
5. Refine language
6. Test again
7. Repeat until satisfied

### Quality Indicators
- ✅ Clear and unambiguous
- ✅ Specific and focused
- ✅ Includes relevant context
- ✅ Defines success criteria
- ✅ Provides examples (if helpful)
- ✅ Specifies output format

### Common Pitfalls to Avoid
- ❌ Too vague or broad
- ❌ Missing context
- ❌ Conflicting instructions
- ❌ Unrealistic expectations
- ❌ No success criteria
- ❌ Ignoring AI limitations

## Template Customization Guide

### For Beginners
1. Use pre-built templates as-is
2. Focus on filling in placeholders
3. Keep prompts simple and direct
4. Test and iterate frequently

### For Intermediate Users
1. Customize templates to your needs
2. Combine multiple prompt patterns
3. Add domain-specific context
4. Create your own templates

### For Advanced Users
1. Build complex, multi-step prompts
2. Create prompt libraries for reuse
3. Develop domain-specific frameworks
4. Optimize for specific AI models

## Usage Examples

### Example 1: Flutter App Feature
```
Input: "I need to add user authentication to my Flutter app"

Generated Prompt:
"Implement user authentication in a Flutter app with the following requirements:
- Authentication Methods: Email/password, Google Sign-In, Apple Sign-In
- State Management: Riverpod for auth state
- Persistence: Keep user logged in across app restarts
- Security: Secure token storage using flutter_secure_storage
- Error Handling: User-friendly error messages
- UI: Login screen with form validation

Provide:
1. Complete authentication service implementation
2. Riverpod providers setup
3. UI implementation with form validation
4. Error handling strategy
5. Testing approach
6. Example usage in widgets"
```

### Example 2: Flutter Game Mechanic
```
Input: "I want to add a jumping mechanic to my platformer game"

Generated Prompt:
"Implement a jumping mechanic for a 2D platformer game in Flutter using Flame:

Requirements:
- Jump Types: Single jump, variable height (based on button press duration)
- Physics: Realistic gravity and jump arc
- Input: Touch/screen tap for jump
- Visual Feedback: Jump animation, dust particles on landing
- Audio: Jump sound effect, landing sound
- Controls: Variable jump height based on press duration

Include:
1. Player component with jump logic
2. Physics implementation (gravity, velocity)
3. Input handling for variable jump
4. Animation system for jump states
5. Particle effects for landing
6. Audio integration
7. Example usage
8. Performance optimizations"
```

### Example 3: Business Strategy
```
Input: "Help me create a marketing strategy for my new mobile app"

Generated Prompt:
"Develop a comprehensive marketing strategy for a new mobile app launch:

App Details:
- Type: [productivity/game/social/etc.]
- Target Audience: [demographics, behaviors]
- Unique Value: [key differentiators]
- Platforms: [iOS/Android/both]

Marketing Goals:
- User Acquisition: [target number of users]
- Engagement: [retention goals]
- Monetization: [revenue model]

Budget: [total marketing budget]
Timeline: [pre-launch, launch, post-launch phases]

Provide:
1. Market analysis and positioning
2. Target audience personas
3. Marketing channel strategy
4. Content marketing plan
5. User acquisition tactics
6. Retention and engagement strategies
7. Budget allocation
8. KPIs and measurement framework
9. Launch timeline
10. Risk mitigation strategies"
```

## Troubleshooting

### Issue: Generated prompts are too vague
**Solution:** Add more specific context and requirements to your input

### Issue: Prompts don't match my use case
**Solution:** Use domain-specific templates and customize placeholders

### Issue: AI responses don't meet expectations
**Solution:** Refine prompt with more constraints and examples

### Issue: Prompts are too complex
**Solution:** Break into multiple simpler prompts

## Advanced Features

### Multi-Step Prompts
Create sequences of prompts for complex tasks:
1. Analysis prompt
2. Strategy prompt
3. Implementation prompt
4. Testing prompt
5. Refinement prompt

### Prompt Chaining
Connect multiple prompts where output of one becomes input for the next

### Conditional Prompts
Create prompts that adapt based on specific conditions or previous responses

### Template Variables
Use placeholders for reusable templates:
- `[TOPIC]` - Main subject
- `[AUDIENCE]` - Target audience
- `[LENGTH]` - Desired length
- `[TONE]` - Tone/style
- `[FORMAT]` - Output format

## Feedback & Improvement

To improve this skill:
1. Try generated prompts with various AI tools
2. Note which prompt structures work best
3. Suggest new templates or categories
4. Report any issues or ambiguities
5. Share successful prompt examples

## Notes

- This skill works best with specific, well-defined inputs
- More context leads to better prompts
- Iterate and refine based on results
- Save successful prompts as templates
- Adapt templates to your specific needs
- Consider the AI model's capabilities and limitations
