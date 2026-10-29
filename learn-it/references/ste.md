# Writing in STE style (ASD-STE100, "80%" by default)

ASD-STE100 (Simplified Technical English) is a controlled language from the aerospace industry. It exists so that maintenance technicians, many of them non-native English speakers, read a procedure fast and do not misread it. The same properties help a learner: little ambiguity, little parsing effort, and no smooth phrasing that hides a gap in the explanation.

## Contents

1. Core rules
2. Korean rules (STE-ko)
3. 80% (default) and strict mode
4. Word substitutions
5. Before and after
6. Self-check

## 1. Core rules

**Words**

1. One word, one meaning. Use the same term for the same thing every time. Variety costs the reader: a new word signals a new thing.
2. Define each technical term at first use, in one sentence.
3. Use short, common words (see section 4).
4. Use concrete words and real values: not "very fast" but "about 10 times faster at 4,000 tokens".
5. Do not stack more than 3 nouns. "Key generation function call overhead" becomes "the overhead of a call to the key generation function".

**Verbs**

6. Use the active voice and name the actor. The passive voice hides who does what, and in an algorithm or a protocol, who does what is the content.
7. Use simple tenses. Use the present tense for how things work.
8. Do not turn verbs into nouns: "perform an evaluation of" becomes "evaluate".

**Sentences**

9. One idea per sentence. Maximum about 20 words in a procedure step and about 25 words in a description.
10. Do not remove words to make a sentence shorter. Keep "the", "a", "that", and connectors. Telegraphic text is harder to parse, not easier.
11. Use a vertical list for 3 or more parallel items, and for any sequence.
12. Connect related sentences with a clear connector: "because", "so", "then", "but".

**Paragraphs**

13. One topic per paragraph. Start with the topic sentence. Maximum about 6 sentences.
14. Give only the information that the reader needs for the current goal. Move side facts into a note, or remove them.

**Procedures**

15. One action per step (two only if they occur at the same time). Use the imperative.
16. Put the condition before the action: "If the proof fails, reject the input."
17. Notes give information, not instructions. A warning comes before the step that it applies to.

## 2. Korean rules (STE-ko)

STE는 영어용 규격이다. 한국어에는 규칙의 목적을 옮겨 적용한다.

1. **한 문장에 한 생각.** 서술어 하나가 문장을 끝낸다. 한 문장에 연결어미(-고, -며, -는데, -지만, -므로, -면서, 조건의 -면)는 하나까지 둔다. 즉 절은 둘까지다. 길이는 공백을 포함해 설명문 약 60자, 절차문(지시) 약 40자다. 넘으면 나눈다. 결과나 예시 단계를 늘어놓는 번호 목록은 설명문 기준을 따른다.
2. **용어 하나에 뜻 하나.** 처음 나올 때 정의하고 원어를 한 번 병기한다: "커밋먼트(commitment)는 값을 숨긴 채 고정하는 값이다." 이후에는 같은 개념을 다른 말(약속값, 커밋 등)로 바꾸지 않는다.
3. **행위자를 밝힌다.** 한국어는 주어를 자주 생략한다. 누가 하는지가 내용이면 주어를 쓴다: "증명자가 r을 고른다. 검증자는 r을 모른다."
4. **능동형으로 쓴다.** "~되어진다", "~에 의해 ~된다", "~하게 된다"를 피한다. "서명이 생성된다"는 "서명자가 서명을 만든다"로 쓴다.
5. **지시어 대신 명사를 쓴다.** "이것", "그것", "이는", "해당"을 줄이고 명사를 반복한다. STE에서 반복은 결함이 아니라 명확성이다.
6. **명사 나열은 셋까지.** "검증 키 생성 함수 호출 비용"은 "검증 키를 만드는 함수를 부르는 비용"으로 쓴다.
7. **모호한 정도 표현을 지운다.** "매우", "상당히", "다소", "어느 정도", "~라고 할 수 있다", "~인 것으로 보인다" 대신 수치를 쓰거나 단정한다. 모르면 모른다고 쓴다: "이 값은 논문에 나오지 않는다."
8. **번역투를 피한다.** 섹션 4의 표를 따른다.
9. **문체를 통일한다.** 설명은 "~다" 평서문으로 쓴다. 절차는 번호 목록으로 쓰고, 한 단계에 동작 하나만 둔다: "1. 입력 x를 해시한다."
10. **영어 용어.** 정착된 한국어 용어가 있으면 한국어로 쓰고, 첫 등장에만 원어를 병기한다. 정착된 한국어 용어가 없으면 원어를 쓴다(예: KV 캐시, softmax). 원어 병기는 독자가 문헌에서 원어로 다시 만날 용어에만 한다. 리더, 팔로워처럼 영어를 소리대로 적은 말은 병기하지 않아도 된다. 한 문장에 영어 괄호는 하나까지만 두고, 더 필요하면 문장을 나눈다.

## 3. 80% (default) and strict mode

The default "80%" mode allows these relaxations. Use them only when they help understanding:

- Technical terms of the domain are fine. Define them at first use.
- One clearly labeled analogy per idea ("비유:" / "Analogy:"). Put it after the literal explanation, never in place of it, and say where the analogy breaks.
- A formal definition or a theorem can be longer than the length limit. Keep it exact rather than short.
- The passive voice is fine when the actor is unknown or does not matter.
- A question can open a section ("왜 캐시가 필요한가?"), because it sets up the next idea.

Naming STE alone ("STE로", "in STE") means this default mode.

Strict mode, when the user asks for "strict STE", "100% STE", or "STE 그대로":

- No relaxations: no analogies and no rhetorical questions.
- In English, prefer words from the STE approved dictionary, and keep to the length limits exactly.
- Procedures use only imperative sentences.

## 4. Word substitutions

English:

| Instead of | Write |
|---|---|
| utilize, leverage, employ | use |
| facilitate, enable | help, make possible |
| demonstrate, illustrate | show |
| obtain, acquire, retrieve | get |
| initiate, commence | start |
| terminate, cease | stop |
| approximately, roughly | about |
| subsequently | then, after this |
| prior to | before |
| in order to | to |
| perform an analysis of | analyze |
| a large number of | many, or the real number |
| it should be noted that, basically, essentially, simply | (delete) |

한국어 (번역투):

| 피할 표현 | 쓸 표현 |
|---|---|
| ~에 대한 설명을 한다 | ~를 설명한다 |
| ~를 통해 | ~로 |
| ~하는 것이 가능하다 | ~할 수 있다 |
| ~를 가진다 | ~가 있다 |
| ~에 있어서 | ~에서 |
| ~되어진다, ~하게 된다 | 능동형: ~가 ~한다 |
| ~라고 할 수 있다, ~인 것으로 보인다 | 단정하거나 근거를 쓴다 |
| 매우, 상당히, 다소 | 수치 |

## 5. Before and after

**Description (English)**

Before: "Leveraging a KV cache substantially accelerates autoregressive inference by obviating the redundant recomputation of attention keys and values for previously processed tokens, which is very important for long contexts."

After:
"A transformer makes text one token at a time. To make each new token, attention uses the keys and values of all earlier tokens. Without a cache, the model calculates these keys and values again at every step. A KV cache keeps them in memory, so the model calculates keys and values only for the new token. At token 1,000, the model calculates keys and values for 1 token instead of 1,000. Attention still reads all 1,000 cached keys and values."

**Description (Korean)**

Before: "KV 캐시는 이전 토큰들에 대한 키와 밸류의 중복 계산을 제거함으로써 자기회귀 추론의 속도를 상당히 향상시키는 것을 가능하게 해주며, 이는 특히 긴 컨텍스트에서 매우 중요하다고 할 수 있다."

After:
"트랜스포머는 토큰을 하나씩 만든다. 새 토큰을 만들 때 어텐션(attention)은 앞선 모든 토큰의 키(key)와 값(value)을 쓴다. 캐시가 없으면 모델은 단계마다 앞선 토큰의 키와 값을 다시 계산한다. KV 캐시는 계산한 키와 값을 메모리에 저장한다. 그래서 모델은 새 토큰 하나의 키와 값만 계산한다. 1,000번째 토큰에서 모델은 키와 값을 1,000개가 아니라 1개만 계산한다. 어텐션은 여전히 저장된 키와 값 1,000개를 모두 읽는다."

**Procedure (English)**

Before: "Make sure that the environment variable has been set correctly and then go ahead and restart the server; if you happen to run into errors, it might be a good idea to take a look at the logs."

After:
1. Make sure that `API_KEY` is set.
2. Restart the server.
3. If the server shows an error, read `logs/server.log`.

**Procedure (Korean)**

Before: "먼저 환경 변수가 제대로 설정되어 있는지 확인하신 후에 서버를 재시작해주시면 되는데, 만약 에러가 발생하게 되는 경우에는 로그를 확인해보시는 것이 좋습니다."

After:
1. 환경 변수 `API_KEY`가 있는지 확인한다.
2. 서버를 다시 시작한다.
3. 오류가 나면 `logs/server.log`를 연다.

## 6. Self-check

First run the mechanical pass: `python3 <skill>/scripts/ste_check.py <file>` (Markdown, HTML, or a narration `script.json`). It flags long sentences, chained clauses, vague words, translationese, and passives. It only finds candidates: a formal definition can be long on purpose.

Then read the text once with only these questions:

- Does each term mean one thing, and is it defined at first use?
- Does any sentence carry two ideas? Look for long "and" chains, or chains of "-고 / -며 / -는데".
- Is the actor named wherever the actor matters?
- Did a vague word ("very", "some", "상당히") survive where a number fits?
- Is every analogy labeled, and does it come after the literal explanation?
