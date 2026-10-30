## Requirements: Customer Review Handler

**Goal:** ek graph jo customer review le, uska sentiment nikaale, aur sentiment ke hisaab se alag-alag reply banaye. Code tum likhoge, to yaha sirf _kya chahiye_ hai, _kaise_ nahi.

### 1. Input aur output

|        | Detail                                                                                  |
| ------ | --------------------------------------------------------------------------------------- |
| Input  | Ek key: `review` (string)                                                               |
| Output | Final state jisme `sentiment` aur `response` hon. Negative review me `diagnosis` bhi ho |

### 2. State fields

| Field       | Type                                   | Kab set hoti hai        |
| ----------- | -------------------------------------- | ----------------------- |
| `review`    | str                                    | Input se                |
| `sentiment` | sirf `"positive"` ya `"negative"`      | Hamesha                 |
| `diagnosis` | dict (`issue_type`, `tone`, `urgency`) | Sirf negative path me   |
| `response`  | str                                    | Hamesha, aakhri node me |

### 3. Behaviour

**Step 1, sentiment nikalo:** LLM review padh ke sirf `positive` ya `negative` bataye. Output free text nahi, **validated structured output** hona chahiye, taki koi aur string aa hi na sake.

**Step 2, branch karo:** sentiment ke hisaab se ek hi raasta chalna chahiye. Dono kabhi nahi.

**Positive path (1 step):**

- 3-4 sentence ka warm thank-you.
- Reply me user se website pe feedback dene ko kaho.

**Negative path (2 steps):**

1. _Diagnosis:_ LLM teen cheezein nikaale, teeno fixed options me se:
   - `issue_type`: UX, Performance, Bug, Support, Other
   - `tone`: angry, frustrated, disappointed, calm
   - `urgency`: low, medium, high
2. _Reply:_ diagnosis ko prompt me use karke 4-5 sentence ka empathetic reply, jisme:
   - frustration acknowledge ho,
   - apology ho,
   - concrete next steps hon,
   - reply ka tone urgency se match kare (high urgency me zyada fast aur seedha).

### 4. Non-functional requirements

- Branching ka decision ek alag chhote function me ho, jo sirf state padhe. Wo LLM ko call nahi karega.
- Dono branches ke baad graph `END` pe khatam ho.
- Graph draw karke dekhne par conditional edges dikhni chahiye, yani routing ka type declare kiya ho (pichli baat yaad karo).
- Model ya API key code me hardcoded na ho.

### 5. Acceptance tests

Ye sab pass hone chahiye, tabhi kaam khatam.

| #   | Input                                                             | Expected                                                                                        |
| --- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 1   | Clear positive review                                             | `sentiment = positive`, `response` me thank-you aur feedback request, `diagnosis` key **nahi**  |
| 2   | Login bug wali negative review                                    | `sentiment = negative`, `diagnosis` me teeno fields valid, `response` diagnosis ko reflect kare |
| 3   | Ek aur negative review jo bug nahi balki pricing ya support ki ho | `issue_type` bug na aaye (LLM ki accuracy check karna)                                          |
| 4   | Mixed review: "UI accha hai, lekin app roz crash hota hai"        | Koi ek valid branch chale, crash na ho. Batao kaunsa chala                                      |
| 5   | Khali string `""`                                                 | Graph crash na kare (batao kya hota hai)                                                        |
| 6   | Graph ka drawing                                                  | Mermaid output me `find_sentiment` se do dotted edges dikhen                                    |

### 6. Stretch goal (optional)

`neutral` ko teesra sentiment banao. Neutral review pe: ek chhota acknowledgement bhejo aur user se aur details maango, diagnosis ke bina. Isme schema, router, aur graph, teeno jagah badlav aayega, to dekho kitni jagah touch karni padi.

### 7. Jab ready ho to mujhe bhejo

1. Poora code.
2. Test 1, 2 aur 4 ka output (sentiment, diagnosis, response).
3. Test 5 ka result, aur ye ki tumne kya kiya.
4. Test 6 ka mermaid output.

Mixed review (test 4) ke baare me ye bhi batana ki LLM ka faisla tumhe sahi laga ya nahi aur kyun. Review main code aur outputs dono ka karunga.
