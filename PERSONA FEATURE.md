# Persona System

Replaces the old `/system` command. Allows each chat session to be defined and customized using a **named persona**, composed of up to **10 system prompt slots** (0–9). These slots are combined and sent to the model as a single prompt at runtime.

---

## 📂 Storage

Each persona is saved as a `.json` file in:

```
.hiollama/persona/
```

The filename is the **persona name**, and it contains:

* The name of the persona
* The content of each system prompt slot (0–9)

---

## 🧠 Persona Concept

* **Persona Name**: A label for the identity or purpose of the AI in a chat.
* **Prompt Slots (0–9)**: Modular prompt entries to build up the persona in layers.

  * Example: Slot 0 = identity, 1 = role, 2 = behavior rules, etc.
* **Combined Prompt**: When sending to the model, all non-empty slots are concatenated into a single system prompt.

---

## 🛠️ Commands

### 🔧 Editing

```bash
/persona.set <slot> <text>       # Set a system prompt at slot 0–9
/persona.get <slot>              # View contents of a specific slot
/persona.clear <slot>            # Clear contents of a specific slot
```

### 🎭 Identity

```bash
/persona.name <name>             # Set the persona name
/persona.show                    # Show current name + all slot contents
/persona.reset                   # Clear name and all slot contents (start fresh)
```

### 💾 Persistence

```bash
/persona.save                    # Save current persona (uses name as filename)
/persona.load <name>             # Load a saved persona by name
/persona.list                    # List all saved personas
/persona.delete <name>           # Delete a saved persona
```
## 📌 Notes

* You must set a persona name before saving.
* Empty slots are ignored in the final system prompt.
* Slot values can be multiline if supported by your input interface.

---

Potential Implementation Considerations

Error handling: What happens if persona name contains invalid filename characters?

Hmm, thats a good question, what do you think is best?

Validation: Should there be checks for slot numbers (0-9 range)?

What do you mean? It is not requierd that all slots be filled, and the code should not assume that they are.

Overwrite protection: Should /persona.save warn before overwriting existing personas?

Yes

Current state tracking: How does this integrate with existing chat channels?

Each chat will have their own persona data--the persona name and the 10 slots, just like each chat has a system prompt now.

Integration Questions

How does this replace the old /system command in existing chat sessions?

The old system prompt will be removed, no need for backwwards compatibility.

Do chat channels automatically get a default persona, or start empty?

For now they start empty, we might change this later

Does the /twist command carry over persona context between channels?

No, it should work exactly as it is right now.

Minor Documentation

The "Combined Prompt" bullet point appears cut off in the concept section
Might be helpful to include a usage example showing slot 0-2 building a complete persona

✅ Good Join (line breaks):

ie.

You are a helpful assistant.

You speak like a pirate.

You are concise.

Each instruction is clear and independent. The model knows how to chunk these semantically.

✅ So, best practice:
Use \n\n (double line breaks) to signal separate instructions:


final_prompt = "\n\n".join([p for p in prompts if p.strip()])

That preserves clarity and plays to the model's strengths — it's used to reading prompts structured like natural documents.

