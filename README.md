# Baby Berry — Alexa Skill

An Alexa skill for logging baby tracking events to [Huckleberry](https://huckleberrycare.com) by voice.

**Invocation name:** baby berry

---

## Setup

### Prerequisites
- [Huckleberry](https://huckleberrycare.com) account with at least one child
- [Amazon Developer](https://developer.amazon.com) account (free)
- [AWS](https://aws.amazon.com) account (free tier is sufficient)
- [pyenv](https://github.com/pyenv/pyenv) installed

### 1. Clone & set up the environment
```bash
git clone https://github.com/JohnG210/baby-berry.git
cd baby-berry
./setup_venv.sh
```

### 2. Create your credentials file
```bash
cp .env.example .env
```
Edit `.env` with your values:
```
HUCKLEBERRY_EMAIL=you@example.com
HUCKLEBERRY_PASSWORD=yourpassword
HUCKLEBERRY_CHILD_UID=your_child_uid
HUCKLEBERRY_TIMEZONE=America/New_York
```

To find your `HUCKLEBERRY_CHILD_UID`, run:
```bash
source skill/.venv/bin/activate
python -c "
from huckleberry_api import HuckleberryAPI
import os
api = HuckleberryAPI(os.environ['HUCKLEBERRY_EMAIL'], os.environ['HUCKLEBERRY_PASSWORD'], os.environ['HUCKLEBERRY_TIMEZONE'])
api.authenticate()
print(api.get_children())
"
```

### 3. Create the Alexa skill
1. Go to [developer.amazon.com](https://developer.amazon.com) → Alexa Developer Console → **Create Skill**
2. Name: `Baby Berry`, type: **Custom**, host: **Provision your own**
3. In the **Interaction Model** tab → JSON Editor → paste the contents of `skill/interaction_model.json` → **Save** → **Build**
4. Note your **Skill ID** from the skill settings page

### 4. Deploy the Lambda function
```bash
# Build the deployment zip
cd skill && ./build.sh && cd ..

# Create the Lambda function (replace placeholders)
aws lambda create-function \
  --function-name baby-tracker \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_LAMBDA_ROLE \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://skill/deployment.zip \
  --timeout 30 \
  --memory-size 256

# Set environment variables
aws lambda update-function-configuration \
  --function-name baby-tracker \
  --environment "Variables={
    HUCKLEBERRY_EMAIL=you@example.com,
    HUCKLEBERRY_PASSWORD=yourpassword,
    HUCKLEBERRY_CHILD_UID=your_child_uid,
    HUCKLEBERRY_TIMEZONE=America/New_York
  }"

# Allow Alexa to invoke the Lambda (replace with your Skill ID)
aws lambda add-permission \
  --function-name baby-tracker \
  --statement-id alexa-skill-trigger \
  --action lambda:InvokeFunction \
  --principal alexa-appkit.amazon.com \
  --event-source-token amzn1.ask.skill.YOUR_SKILL_ID
```

### 5. Connect Lambda to the Alexa skill
1. In the Alexa Developer Console → **Endpoint** tab
2. Select **AWS Lambda ARN**
3. Paste your Lambda ARN (find it with `aws lambda get-function --function-name baby-tracker --query Configuration.FunctionArn`)
4. **Save** → go back and **Build** the model

### 6. Test
In the Alexa Developer Console → **Test** tab → enable **Development** mode, then type:
```
open baby berry
```

Or on any Alexa device signed in to the same Amazon account:
```
Alexa, tell baby berry to log 4 oz formula bottle
```

### Updating after code changes
```bash
cd skill && ./build.sh && cd ..
aws lambda update-function-code --function-name baby-tracker --zip-file fileb://skill/deployment.zip
```

---

## How to Use

### One-shot (recommended)
> "Alexa, tell baby berry to **log 60 ml bottle at seven oh seven pm**"

### Session mode
> "Alexa, open baby berry"
> *(then speak a command)*

---

## Bottle Feeding

Log a bottle feeding with amount, unit, type, and optional time.

| Say | Result |
|---|---|
| "log 4 oz bottle" | 4 oz Formula (now) |
| "log 60 ml bottle" | 60 ml Formula (now) |
| "log 4 oz formula bottle" | 4 oz Formula (now) |
| "log 60 ml breast milk bottle" | 60 ml Breast Milk (now) |
| "log 4 oz mixed bottle" | 4 oz Mixed (now) |
| "log 60 ml bottle at seven oh seven pm" | 60 ml Formula at 7:07 PM today |
| "log 4 oz formula bottle at two thirty pm" | 4 oz Formula at 2:30 PM today |

**Units:** oz, ounces / ml, milliliters
**Types:** formula *(default)*, breast milk, mixed
**Time:** any time today in 12-hour or 24-hour format

---

## Nursing / Breastfeeding

Track a nursing session from start to finish.

| Say | Result |
|---|---|
| "start nursing" | Start nursing (defaults to left side) |
| "start nursing on the left" | Start nursing, left side |
| "start nursing on the right" | Start nursing, right side |
| "start feeding on the left side" | Start nursing, left side |
| "switch side" | Switch to the other breast |
| "other side" | Switch to the other breast |
| "pause nursing" | Pause the session |
| "resume nursing" | Resume the session |
| "done nursing" | Save and complete the session |
| "stop nursing" | Save and complete the session |
| "cancel nursing" | Discard the session |

---

## Sleep

Track a sleep session from start to finish.

| Say | Result |
|---|---|
| "baby is sleeping" | Start sleep session |
| "baby fell asleep" | Start sleep session |
| "put baby down" | Start sleep session |
| "baby woke up" | Save and complete sleep session |
| "baby is awake" | Save and complete sleep session |
| "stop sleep" | Save and complete sleep session |
| "pause sleep" | Pause the session |
| "resume sleep" | Resume the session |
| "cancel sleep" | Discard the session |

---

## Diapers

Log a diaper change with optional detail.

| Say | Result |
|---|---|
| "log a wet diaper" | Pee diaper |
| "log a pee diaper" | Pee diaper |
| "log a poo diaper" | Poo diaper |
| "log a dirty diaper" | Poo diaper |
| "log a both diaper" | Pee + poo |
| "log a dry diaper" | Dry / unchanged |
| "diaper change" | Prompts for type |
| "log a yellow poo diaper" | Poo, yellow color |
| "log a poo diaper that is runny" | Poo, runny consistency |
| "log a poo diaper with a rash" | Poo, rash noted |
| "log a poo diaper with no rash" | Poo, no rash noted |

**Colors:** yellow / golden / mustard, green / greenish / olive, brown / brownish / tan, black / dark / meconium, red / reddish / bloody, gray / grey
**Consistency:** solid / firm / formed, loose / soft / mushy, runny / liquid / watery, mucousy / slimy / mucus, hard / constipated, pebbles / pellets, diarrhea / explosive

---

## Growth

Log weight, height, and/or head circumference. Defaults to imperial (lbs / inches); converted to metric before saving.

| Say | Result |
|---|---|
| "log weight 8 pounds" | Weight: 8 lbs |
| "log weight 8" | Weight: 8 lbs (imperial assumed) |
| "log height 21 inches" | Height: 21 in |
| "log head circumference 14" | Head: 14 in |
| "log weight 4 in metric" | Weight: 4 kg |
| "log height 55 in metric" | Height: 55 cm |
| "log growth weight 8 height 21" | Weight + height together |

**Unit systems:** imperial *(default)* — lbs, inches / metric — kg, cm
