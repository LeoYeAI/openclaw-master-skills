# Text Processing Principle

## **Quick Summary:**

This document provides detailed guidelines for converting raw text into voice synthesis scripts (`segments.json`).

**For the complete 4-step workflow with examples**, see **Step 2** in [SKILL.md](SKILL.md), which includes:
- Step 2.1: Text Segmentation and Role Analysis
- Step 2.2: Voice Selection
- Step 2.3: Emotions Segmentation
- Step 2.4: Check and Post-processing

This document serves as a **detailed reference** for the preprocessing workflow in Step 2 of SKILL.md.

---

## **General Guideline:**

This document provides detailed guidelines for converting raw text into voice synthesis scripts (`segments.json`). Follow these four essential steps:

### Overall Steps:

**Step 1: Text Segmentation and Role Analysis**
First, segment your text into logical units and identify the role/character for each segment. Consult [Section-1](#1-text-segmentation-and-role-analysis) below to understand:
- **When to split** segments (speaker changes, dialogue vs. narration)
- **When NOT to split** (continuous narration, quoted speech)
- Create preliminary `segments.json` with role labels (voice_id to be filled later)
- Key principle: split by **logical unit**, not just by sentence

**Step 2: Voice Selection**
After segmenting and labeling roles, analyze all detected characters in your text. Consult [voice_catalog.md](reference/voice_catalog.md) to match voices to characters based on:
- The **language** of each segment
- The **character traits** (age, gender, personality, role)
- The **use case scenario** (podcast, audiobook, announcement, etc.)
- Fill in the `voice_id` for each role in `segments.json`

**Step 3: Emotions Segmentation** *(For non-2.8 series models only)*
For models other than speech-2.8 series, analyze emotions in your segments:
- For **long segments**, split further based on **emotional transitions**
- Add appropriate **emotion tags** to each segment
- Refer to [Section-3](#3-emotions-segmentation-and-add-emotion-tags-only-for-models-other-than-speech-28-series) for emotion tags and examples
- Skip this step for speech-2.8 models (emotion is auto-matched)

**Step 4: Check and Post-processing**
Finally, review and optimize your script:
- Verify segment length limits (async TTS ≤1,000,000 characters)
- Clean up conversational text (remove speaker names if needed)
- Ensure consistency in voice and emotion tags
- **Critical check**: For multi-voice content (audiobooks, fiction, etc.), verify that narration and dialogue in the same sentence are properly split (see [Section-1](#1-text-segmentation-and-role-analysis) for examples)


### **Segmentation Rules for Different Models:**
**For speech-2.8 models:**
- Split when different speakers need different voices
- Set `emotion` to empty string `""` for auto-matching

**For other models:**
- Split when voice changes
- Split when emotion changes significantly
- Each segment needs valid emotion tag


### **`segments.json` format:**

Each segment requires:
- `text`: The segment content
- `role`: Character/role label (narrator, male_character, female_character, host, guest, etc.)
- `voice_id`: Voice to use (see [voice_catalog.md](reference/voice_catalog.md))
- `emotion`: Emotion tag (use `""` for speech-2.8 auto-matching)

Save to `segments.json` for the next step.


---

## **1. Text Segmentation and Role Analysis:**

### **Key principle (Important!): Split by logical unit, NOT simply by sentence**

#### **When to split (Important!):**
- Different speakers clearly marked
- Narrator vs. character dialogue in (in fiction/audiobooks/interview etc.)
- In some scenarios (like audiobooks, multi-voice fiction etc.), where speaker's identity is important, split when narration and dialogue mix in the same sentence. (See `Example1` below)

#### **When NOT to split (Important!):**
- Third-person narration like "John said..." or "The reporter noted..."
- Quoted speech in narration (in documentary/podcast/report etc.) should keep in narrator's voice
- Keep in narrator's voice unless specific characterization is needed

### **Decision depends on use case:**

| Use case | Example | Split strategy |
|----------|---------|----------------|
| **Podcast/Interview** | "Host: Welcome to the show. Guest: Thank you for having me." | Split by speaker |
| **Documentary narration** | "The scientist explained, 'The results are promising.'" | Keep as one segment (narrator voice) |
| **Audiobook/Fiction** | "'Who's there?' she whispered." | Split: "'Who's there?'" should be in character voice, while "she whispered." should be in narrator's voice |
| **Report** | "According to the report, the economy is growing." | Keep as one segment |


### **Examples:**
**Example1: Audiobook with characters (speech-2.8)**
In audiobooks (multi-voice fiction), split when narration and dialogue mix in the same sentence:
```json
[
  {"text": "The detective entered the room.", "role": "narrator", "voice_id": "", "emotion": ""},
  {"text": "\"Who's there?\"", "role": "female_character", "voice_id": "", "emotion": ""},
  {"text": "she whispered.", "role": "narrator", "voice_id": "", "emotion": ""},
  {"text": "\"It's me,\"", "role": "male_character", "voice_id": "", "emotion": ""},
  {"text": "he replied calmly.", "role": "narrator", "voice_id": "", "emotion": ""}
]
```

**Example2: Documentary/podcast narration (speech-2.8)**
Quoted speech in narration stays in narrator's voice (no need to split):
```json
[
  {
    "text": "The scientist explained, \"The results show significant improvement in all test groups.\"",
    "role": "narrator",
    "voice_id": "",
    "emotion": ""
  },
  {
    "text": "According to the latest report, the economy has grown by 3% this quarter.",
    "role": "narrator",
    "voice_id": "",
    "emotion": ""
  }
]
```

**Note:** In the preliminary `segments.json` created in this step:
- Fill in the `text` field with segment content
- Fill in the `role` field to identify the character (narrator, male_character, female_character, host, guest, etc.)
- Leave `voice_id` empty (to be filled in Step 2)
- Leave `emotion` empty for speech-2.8 models


## **2. Voice Selection:**

When selecting voices for each segment, must consult [voice_catalog.md](reference/voice_catalog.md) for detailed voice characteristics. Consider the following factors:

- **Language**: Match voice to the text language (Chinese, English, etc.)
- **Use case scenario**:
  - **Podcast/Interview**: Professional, clear voices for hosts and guests
  - **Audiobook/Narrative**: Expressive voices for narration and character dialogue
  - **Notifications/Announcements**: Neutral, authoritative voices
  - **Marketing/Advertising**: Energetic, engaging voices
- **Character traits** (for multi-character content):
  - Age: Child, adult, elderly
  - Gender: Male, female
  - Personality: Serious, cheerful, mysterious, etc.
  - Role: Narrator, protagonist, antagonist, supporting characters

**Action Required:** After analyzing all roles detected in Step 1, match each role to an appropriate voice_id from the catalog and update the `segments.json` file accordingly.


## **3. Emotions Segmentation and add Emotion Tags (Only for models other than speech-2.8 series):**

### **Requirements explanation:**
- **speech-2.8 series** (speech-2.8-hd and speech-2.8-turbo): auto-matched emotion, just leave `emotion` empty and skip the Emotions Segmentation
- **Other models**: [step1] Pick the long text segment in the `segments.json` and improve it by segmenting them into smaller segments with different emotions. [step2] Then add the emotion tags to each segment in the newly segmented version of `segments.json`.

### **Emotion Tags List:**
- For speech-2.6 series (speech-2.6-hd and speech-2.6-turbo): happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper
- For older models: happy, sad, angry, fearful, disgusted, surprised, calm (7 emotions)

**Example: Specific emotion (speech-2.6)**
```json
[
  {"text": "Great news!", "role": "female-shaonv", "voice_id": "female-shaonv", "emotion": "happy"},
  {"text": "But challenges ahead...", "role": "female-shaonv", "voice_id": "female-shaonv", "emotion": "fearful"}
]
```


## **4. Check and Post-processing:**

- If the text segment is too long (async TTS ≤1,000,000 chars), you can split it into smaller segments.
- If the texts are purely conversational, remove the speaker's name and keep the content.
- Ensure consistency in voice and emotion tags throughout.
- **Critical check for multi-voice content**: For audiobooks, multi-voice fiction, interviews, or any content where speaker identity is important, verify that narration and dialogue mixed in the same sentence are properly split. Refer to `Example1` in Section 1 for the correct format.
