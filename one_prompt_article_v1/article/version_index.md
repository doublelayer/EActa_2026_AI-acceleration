Keep each version as a set: `drafts/article_draft_vN.md`, `article_resources/vN/`, `manuscript_versions/Electrochimica_Acta_research_article_draft_vN.docx`, and `reviews/review_vN.md`. Choose N as one greater than the highest DOCX version already in `manuscript_versions/`; never reuse a version number. The Markdown and DOCX must be content-aligned when generated. Reviewers later edit/comment on the DOCX; replace the matching archived DOCX with that reviewed copy, update its recorded hash as provenance, and regenerate its review record. The record preserves complete DOCX text, tracked edits, and comments for history and the next revision. Other reports, scripts, ledgers, logs and generated data remain in the run folder; do not archive a release review or rolling handoff file. The per-artifact SHA-256 values below are informational provenance; the archive verifier checks that indexed files exist and that archive structure and review-record content are consistent, but does not compare hashes for archived DOCX files, Markdown drafts, PNG images, or `review_vN.md` records. Hash values for Markdown use UTF-8 bytes with LF line endings; PNG, DOCX, and DOCX review records are hashed as stored. `input_manifest.json` is reserved for the five source DASC `.db` files. Store user-supplied review files under their supplied filenames and preserve their wording and bytes.

## DOCX reviews by manuscript version

Each record below contains a complete text projection of its archived DOCX, including tracked insertions and deletions, plus every embedded Word comment with its anchor. It records source DOCX and embedded XML hashes as informational provenance. The source DOCX remains authoritative for layout and figures. For new reviews, replace the repository's DOCX with the reviewed copy before the next generation run, update the recorded DOCX hash as provenance, and regenerate `reviews/review_vN.md`. The archive verifier does not compare any of these hashes; it checks review structure, counts, comment IDs, and transcript equality with the source DOCX. `reviews/review_index.md` lists each version and its comment and revision counts.

| Version | Word comments | Tracked insertions | Tracked deletions | Full-DOCX review record | SHA-256 |
|---|---:|---:|---:|---|---|
| v28 | 0 | 0 | 0 | [`reviews/review_v28.md`](reviews/review_v28.md) | `739fb88b98ac0a3ac82eb2a541185d1af50c1950b8e7ff572b9907e61ca25db8` |
| v29 | 0 | 0 | 0 | [`reviews/review_v29.md`](reviews/review_v29.md) | `37c4b3a052840bfccb0873a85f5ee346d4524ff9bf7cb115f2029bd31c08938f` |
| v30 | 0 | 418 | 426 | [`reviews/review_v30.md`](reviews/review_v30.md) | `8b66d420bd52a64de3a4c1f17fef152e9ed45099ba9104267e76d62b5bcb6653` |
| v31 | 0 | 0 | 0 | [`reviews/review_v31.md`](reviews/review_v31.md) | `eaf02c057f58b8566c6f9a6e0c712fa5479ef36875387fa6b480f07ad7732813` |
| v32 | 0 | 0 | 0 | [`reviews/review_v32.md`](reviews/review_v32.md) | `bf52a1dae3ea50d648be588f97a1488e12e449ee8eb914cc3022db857be34cff` |
| v33 | 0 | 0 | 0 | [`reviews/review_v33.md`](reviews/review_v33.md) | `9b4d8e6e5a38f15a3a013e103ecf183ebc9ace1da1a08e6ce3e26e46ccd4ef04` |
| v34 | 0 | 0 | 0 | [`reviews/review_v34.md`](reviews/review_v34.md) | `402b858232cfb8721cd75ec30e8bc8d1f8779d03fed5506d351dfd08932376e2` |
| v35 | 22 | 34 | 31 | [`reviews/review_v35.md`](reviews/review_v35.md) | `63da2ed1457c5e6cfbafee75e9e97ef035535c75539d47538c7fa9f66f435c38` |
| v36 | 0 | 0 | 0 | [`reviews/review_v36.md`](reviews/review_v36.md) | `b4c0b5ee5b5d0971577bf43bd5c488811ac7b75295210083ff6279f5818966d1` |
| v37 | 4 | 19 | 13 | [`reviews/review_v37.md`](reviews/review_v37.md) | `89792f176b56ebce4ce3e7eb80266ca45ca835773b44c5b5e8cfe6a685fa49a1` |
| v38 | 0 | 0 | 0 | [`reviews/review_v38.md`](reviews/review_v38.md) | `ad7dca95ac4896f58f2289908ab4651da5436442ffda9eaf65e27d5cb65a0172` |
| v39 | 0 | 310 | 310 | [`reviews/review_v39.md`](reviews/review_v39.md) | `76b8c4bec41c32f626cd1aca65794fac762e2f9140d58e2ee01e21c72c5ae304` |
| v40 | 0 | 336 | 335 | [`reviews/review_v40.md`](reviews/review_v40.md) | `266720ad1985adf73ee13cfc8af56ffe5380127c977f24c0dffe735404ecfea4` |
| v41 | 0 | 337 | 335 | [`reviews/review_v41.md`](reviews/review_v41.md) | `4e2a3793fcdaac9413bde17bdb4f9121c28887c5b583b32a70c6c093808f1de8` |
| v42 | 0 | 321 | 323 | [`reviews/review_v42.md`](reviews/review_v42.md) | `0b8b0435bec8293513a7278f4b8db6315d86ef80104c26df5ed6529cb78932d0` |
| v43 | 1 | 40 | 27 | [`reviews/review_v43.md`](reviews/review_v43.md) | `cccb865a356d70167f9232f82da6d2672b3df40861c261edad8b90de304d4d7e` |
| v44 | 0 | 21 | 24 | [`reviews/review_v44.md`](reviews/review_v44.md) | `3c20d49951ffe247395a772bbab2b35e68f77ccc0f0fe9c937a1919bf2d54515` |
| v45 | 0 | 2 | 4 | [`reviews/review_v45.md`](reviews/review_v45.md) | `3e2c45f4690c963385e0f0f603e7200e8851050a9cb7f4f30e3cb2bc7220ca14` |
| v46 | 0 | 0 | 0 | [`reviews/review_v46.md`](reviews/review_v46.md) | `75424f9a39566768ffd584609c1802d7205e5e323000e449fbffcd5249afb4f4` |
| v47 | 12 | 82 | 59 | [`reviews/review_v47.md`](reviews/review_v47.md) | `8720d1b1865d23e13b9976053f90bad3f45b10ee18466962115f6f5b9b577f87` |
| v48 | 2 | 0 | 0 | [`reviews/review_v48.md`](reviews/review_v48.md) | `a1fbbe42dd96bac5fbccf88ba96ffc5402aee8215125831c6da738c8de80496e` |
| v49 | 13 | 106 | 81 | [`reviews/review_v49.md`](reviews/review_v49.md) | `c57ea0d865b7f2e7bf3efdc0f68aded69f0e8c6c6b3357848427a9af475c88bc` |
| v52 | 0 | 89 | 84 | [`reviews/review_v52.md`](reviews/review_v52.md) | `95ae283b42e3123e9d705e7cf47ca58a56939973d262f6bb2f9eea2d8150e439` |

Review index: [`reviews/review_index.md`](reviews/review_index.md) (SHA-256 `547fb41b563f4837733b2dea57a79118b95826cd564a6aae0d8f7560912d8969`).

## Reconstructed historical archive

Drafts and image assets below were reconstructed from the corresponding immutable source DOCX files in `manuscript_versions/`. The DOCX files remain in that folder. Markdown preserves document reading order, headings, captions, references, and numbered equations. Word layout and some inline styling are represented as Markdown; display equations were converted from Word math markup. Only embedded images referenced in each document are extracted.

### Version 28

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v28.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v28.docx) (SHA-256 `56455dd293a8c5cbc8b724f3a35559c66bc34ac6247e18ae5bd3cb00acce080b`).
- Reconstructed draft: [`drafts/article_draft_v28.md`](drafts/article_draft_v28.md) (SHA-256 `71366007a432ce137769d9f6f30e4a6c31d97152f87ac1d341c9e63fb6ef49b4`).
- Image resources: [`article_resources/v28/`](article_resources/v28/)
  - `Figure_1.png` (SHA-256 `9d4af03d0734ccc2ac5968a35810e7ba17e941064b5d40719df9593c4a4103cd`).
  - `Figure_2.png` (SHA-256 `56fb335d5f1ffb3c2a1b7691fb40f9b9afd22d2f50aa403e2f8a9eaefa9d89d3`).
  - `Figure_3.png` (SHA-256 `81b0a6752bba02b1c88458ec204df328b0f39910a2b4abcc7731e916ffe7ebad`).

### Version 29

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v29.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v29.docx) (SHA-256 `dbc9f41cbc40845cb96cc5450cd4bb34c68180256e248acd27919e23607682a3`).
- Reconstructed draft: [`drafts/article_draft_v29.md`](drafts/article_draft_v29.md) (SHA-256 `3abfee8e381408b23d4116fec2b59bf742debbfc9a3fb808cb5ca63d8b3abe19`).
- Image resources: [`article_resources/v29/`](article_resources/v29/)
  - `Figure_1.png` (SHA-256 `9d4af03d0734ccc2ac5968a35810e7ba17e941064b5d40719df9593c4a4103cd`).
  - `Figure_2.png` (SHA-256 `fa0d2518f73a42f4b1bd3812ab7a897862911076f318c0c5c3760ff55f8e8574`).
  - `Figure_3.png` (SHA-256 `81b0a6752bba02b1c88458ec204df328b0f39910a2b4abcc7731e916ffe7ebad`).

### Version 30

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v30.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v30.docx) (SHA-256 `3bf445e22bba54a56d647ce8dd6070071a25678f7926d62422841c542ab1c770`).
- Reconstructed draft: [`drafts/article_draft_v30.md`](drafts/article_draft_v30.md) (SHA-256 `24b5adc18c86579bc0472a33aa96b02590f961f48338249ca3fe7c9fd2c8e2c6`).
- Image resources: [`article_resources/v30/`](article_resources/v30/)
  - `Figure_1.png` (SHA-256 `9d4af03d0734ccc2ac5968a35810e7ba17e941064b5d40719df9593c4a4103cd`).
  - `Figure_2.png` (SHA-256 `39f2be2a941c169b11e33d9fc20ed941f53fa206e9077bcaed16ca60ada61984`).
  - `Figure_3.png` (SHA-256 `81b0a6752bba02b1c88458ec204df328b0f39910a2b4abcc7731e916ffe7ebad`).

### Version 31

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v31.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v31.docx) (SHA-256 `dce5abe2b404bbc23bbe2c7a9f19607b115e6f560b6faa66f6c6c4c83c39ce93`).
- Reconstructed draft: [`drafts/article_draft_v31.md`](drafts/article_draft_v31.md) (SHA-256 `d6982c6c031298a18d892e34f0d9d4eb9c43bb374bdc884f12c3dbe4d2a3e614`).
- Image resources: [`article_resources/v31/`](article_resources/v31/)
  - `Figure_1.png` (SHA-256 `9d4af03d0734ccc2ac5968a35810e7ba17e941064b5d40719df9593c4a4103cd`).
  - `Figure_2.png` (SHA-256 `39c86baf534574fa7ec113596fdedb13140d19f73aab873bf5f05d7dae5c623e`).
  - `Figure_3.png` (SHA-256 `e2b60e9471bca2deeca37fc0423f298bbc78c9f39b872a65eb3bba15164e1953`).

### Version 32

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v32.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v32.docx) (SHA-256 `e4c90552068a1998c4e870fd4b37fe1e73b4fd79eeab37cf7b3195fa14033d05`).
- Reconstructed draft: [`drafts/article_draft_v32.md`](drafts/article_draft_v32.md) (SHA-256 `5f9eeca9c9c5fdbbf3c1ef1c8813323713e87cf5b1e95897b8e3cbc06963fce3`).
- Image resources: [`article_resources/v32/`](article_resources/v32/)
  - `Figure_1.png` (SHA-256 `b1ab4a7c0ea6f1a97981e2c347c9a120b2621367112b9f4cd535d909bbc3a5c5`).
  - `Figure_2.png` (SHA-256 `b250fe6de14785e00a6c92dbe00c3c6237d8d95785bda8ee17ce4dca01ee2735`).
  - `Figure_3.png` (SHA-256 `e2b60e9471bca2deeca37fc0423f298bbc78c9f39b872a65eb3bba15164e1953`).

### Version 33

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v33.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v33.docx) (SHA-256 `cb068be2bb359d2ef3af843f527b15a522c94c24f40e1f36f14487c7bc797b6f`).
- Reconstructed draft: [`drafts/article_draft_v33.md`](drafts/article_draft_v33.md) (SHA-256 `7324955b1b61f85e565a1246cd66b46b33b3e3be9abddf7b6b651bd01bd35939`).
- Image resources: [`article_resources/v33/`](article_resources/v33/)
  - `Figure_1.png` (SHA-256 `696b797134975874820ccb0aa7b3c77e3adf1796eda05b697b3b6917f4efe9b1`).
  - `Figure_2.png` (SHA-256 `b250fe6de14785e00a6c92dbe00c3c6237d8d95785bda8ee17ce4dca01ee2735`).
  - `Figure_3.png` (SHA-256 `e2b60e9471bca2deeca37fc0423f298bbc78c9f39b872a65eb3bba15164e1953`).

### Version 34

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v34.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v34.docx) (SHA-256 `6fb47836780af5c4abe9e3a5fece19220a667a27adabc01767b24cca16956ca2`).
- Reconstructed draft: [`drafts/article_draft_v34.md`](drafts/article_draft_v34.md) (SHA-256 `240860d623b9924885ffe21d3e66721ffb50ea08e4f02254c787e294a0722332`).
- Image resources: [`article_resources/v34/`](article_resources/v34/)
  - `Figure_1.png` (SHA-256 `171a532ff911ba996d1f08214d0f2f0c541ca43de11a9ff1a551a4c56903412b`).
  - `Figure_2.png` (SHA-256 `b250fe6de14785e00a6c92dbe00c3c6237d8d95785bda8ee17ce4dca01ee2735`).
  - `Figure_3.png` (SHA-256 `e2b60e9471bca2deeca37fc0423f298bbc78c9f39b872a65eb3bba15164e1953`).

### Version 35

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v35.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v35.docx) (SHA-256 `e23b01d962ab913920a2c63f7f16fe682f40e1969a9532dab603a3d9a8e135bd`).
- Reconstructed draft: [`drafts/article_draft_v35.md`](drafts/article_draft_v35.md) (SHA-256 `8df44757aa59e17e879871551e04508b9a7785687078ea6a8fbe846a2b1f7bfa`).
- Image resources: [`article_resources/v35/`](article_resources/v35/)
  - `Figure_1.png` (SHA-256 `766427e746d23229e5b8eb11dc81809f7770242ec549fbb33b60dad0d65b41c5`).
  - `Figure_2.png` (SHA-256 `84f9157a2f49b842d8a5e4453bd8fd6f95b322b8ec6300bf11e09b9f9f9c0d22`).
  - `Figure_3.png` (SHA-256 `0568130e0acd2a102f7f2f793629b0d2e3644e2ed26c3c4b15d0b017c79ef004`).

### Version 36

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v36.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v36.docx) (SHA-256 `fd0a008ccd10790b1c700da47ac4ea1c07fc25c4c36460b2da9d346a1f27a50e`).
- Reconstructed draft: [`drafts/article_draft_v36.md`](drafts/article_draft_v36.md) (SHA-256 `ffbe72150d7a81921019a9da0598fa389c6f59585163434cd957e14c5d62bd1f`).
- Image resources: [`article_resources/v36/`](article_resources/v36/)
  - `Figure_1.png` (SHA-256 `766427e746d23229e5b8eb11dc81809f7770242ec549fbb33b60dad0d65b41c5`).
  - `Figure_2.png` (SHA-256 `84f9157a2f49b842d8a5e4453bd8fd6f95b322b8ec6300bf11e09b9f9f9c0d22`).
  - `Figure_3.png` (SHA-256 `0568130e0acd2a102f7f2f793629b0d2e3644e2ed26c3c4b15d0b017c79ef004`).

### Version 37

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v37.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v37.docx) (SHA-256 `817b2c77226e92b7847ccd2d888bc53f291ceac101d0fa629df11d3fc9650b4c`).
- Reconstructed draft: [`drafts/article_draft_v37.md`](drafts/article_draft_v37.md) (SHA-256 `fc79fffb890db9b4067e1367636d3eb02e58183180bc9437fbd1ed4acb59323f`).
- Image resources: [`article_resources/v37/`](article_resources/v37/)
  - `Figure_1.png` (SHA-256 `766427e746d23229e5b8eb11dc81809f7770242ec549fbb33b60dad0d65b41c5`).
  - `Figure_2.png` (SHA-256 `84f9157a2f49b842d8a5e4453bd8fd6f95b322b8ec6300bf11e09b9f9f9c0d22`).
  - `Figure_3.png` (SHA-256 `0568130e0acd2a102f7f2f793629b0d2e3644e2ed26c3c4b15d0b017c79ef004`).

### Version 38

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v38.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v38.docx) (SHA-256 `d0daec94246ba1156440fa51129870904467961d80a426b95635ac5d65dbdefd`).
- Reconstructed draft: [`drafts/article_draft_v38.md`](drafts/article_draft_v38.md) (SHA-256 `ec36aee684e903fc88909bd173f88e5a3754ef29df0aabbdbe952534d91d4244`).
- Image resources: [`article_resources/v38/`](article_resources/v38/)
  - `Figure_1.png` (SHA-256 `766427e746d23229e5b8eb11dc81809f7770242ec549fbb33b60dad0d65b41c5`).
  - `Figure_2.png` (SHA-256 `84f9157a2f49b842d8a5e4453bd8fd6f95b322b8ec6300bf11e09b9f9f9c0d22`).
  - `Figure_3.png` (SHA-256 `0568130e0acd2a102f7f2f793629b0d2e3644e2ed26c3c4b15d0b017c79ef004`).

### Version 39

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v39.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v39.docx) (SHA-256 `4620ede0212ce357b0aeb11c28491517bebca11e81f3d7da727888368d17e95e`).
- Reconstructed draft: [`drafts/article_draft_v39.md`](drafts/article_draft_v39.md) (SHA-256 `c745e26434c14a3c181d8df6ddc11b02f26b5b93b6cc01b6219ae74ed2c6b1e4`).
- Image resources: [`article_resources/v39/`](article_resources/v39/)
  - `Figure_1.png` (SHA-256 `766427e746d23229e5b8eb11dc81809f7770242ec549fbb33b60dad0d65b41c5`).
  - `Figure_2.png` (SHA-256 `84f9157a2f49b842d8a5e4453bd8fd6f95b322b8ec6300bf11e09b9f9f9c0d22`).
  - `Figure_3.png` (SHA-256 `0568130e0acd2a102f7f2f793629b0d2e3644e2ed26c3c4b15d0b017c79ef004`).

### Version 40

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v40.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v40.docx) (SHA-256 `a76a90ec720736a8269713b1fdafd43075cf1bcc78cb13de9264407d3bb1d835`).
- Reconstructed draft: [`drafts/article_draft_v40.md`](drafts/article_draft_v40.md) (SHA-256 `585aadefa84b613c63cd0caee27ea30d174fd66a0162e58daa57103daf602083`).
- Image resources: [`article_resources/v40/`](article_resources/v40/)
  - `Figure_1.png` (SHA-256 `766427e746d23229e5b8eb11dc81809f7770242ec549fbb33b60dad0d65b41c5`).
  - `Figure_2.png` (SHA-256 `29768fe6080fd257a2cc878f0f912c519e00ca818bf644f600620212ec47f7be`).
  - `Figure_3.png` (SHA-256 `cac1201bd397f40999bbbf7dfab2766ba529851ad38e1bb6112e49e0f71121c6`).

### Version 41

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v41.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v41.docx) (SHA-256 `fcaac67093a44d653cac80b77db49660d047b1d999112d576c4000fe95ce6d23`).
- Reconstructed draft: [`drafts/article_draft_v41.md`](drafts/article_draft_v41.md) (SHA-256 `dee7bf0d145fe4f0e74b91e2e0b6a25c4a3bfad3efcb7baca7863c74c45068c9`).
- Image resources: [`article_resources/v41/`](article_resources/v41/)
  - `Figure_1.png` (SHA-256 `766427e746d23229e5b8eb11dc81809f7770242ec549fbb33b60dad0d65b41c5`).
  - `Figure_2.png` (SHA-256 `29768fe6080fd257a2cc878f0f912c519e00ca818bf644f600620212ec47f7be`).
  - `Figure_3.png` (SHA-256 `cac1201bd397f40999bbbf7dfab2766ba529851ad38e1bb6112e49e0f71121c6`).

### Version 42

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v42.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v42.docx) (SHA-256 `422cf511609ea56b4817886fec68470c16ab6894dad23650879fb3aaf99f7997`).
- Reconstructed draft: [`drafts/article_draft_v42.md`](drafts/article_draft_v42.md) (SHA-256 `55dfe80c57334779d3c41701e6428b1c6bf560fe711fdae68bf67c2978339ac8`).
- Image resources: [`article_resources/v42/`](article_resources/v42/)
  - `Figure_1.png` (SHA-256 `766427e746d23229e5b8eb11dc81809f7770242ec549fbb33b60dad0d65b41c5`).
  - `Figure_2.png` (SHA-256 `00617308a4e18a9eac38822811222cbba5be8a13fd48201478590ea2b1176ab8`).
  - `Figure_3.png` (SHA-256 `cc51cb196c58a357fe1170329ef37df69ae38e7430f8ee1a8b197b23b8b063d4`).

### Version 43

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v43.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v43.docx) (SHA-256 `f813505844c1b0856e65854902282708b70adf3bdca5a3820fa93532b48da1f3`).
- Reconstructed draft: [`drafts/article_draft_v43.md`](drafts/article_draft_v43.md) (SHA-256 `1aa514cf06cd6cc95b54eb09a1d01951b600c0b019eb2cea5981a37af0923f57`).
- Image resources: [`article_resources/v43/`](article_resources/v43/)
  - `Figure_1.png` (SHA-256 `766427e746d23229e5b8eb11dc81809f7770242ec549fbb33b60dad0d65b41c5`).
  - `Figure_2.png` (SHA-256 `cbfc224536abf51ed237994f27e36a3b91197feb3c98d78a2fa0526fa390d5a4`).
  - `Figure_3.png` (SHA-256 `551f31b394815255d6332978663bf69c9d9b1aa003eb22d55df1dc4807a414f2`).

### Version 44

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v44.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v44.docx) (SHA-256 `76679847d0833063ebb7458e185f3c368df7fb565ca6161e176dbfd17fade7bf`).
- Reconstructed draft: [`drafts/article_draft_v44.md`](drafts/article_draft_v44.md) (SHA-256 `8e4d4b96b16ea4dd42a7fd33a92c9a8351f217d8a636f7017bca1c8f7a902f15`).
- Image resources: [`article_resources/v44/`](article_resources/v44/)
  - `Figure_1.png` (SHA-256 `f1c8a2533dbda5b7d025669b0f7efd89026833eecf1f4bd29f6993192fe0ae50`).
  - `Figure_2.png` (SHA-256 `49068cfead55e91871f5470384e368540d2ac277dc616e7ba968547268db42aa`).
  - `Figure_3.png` (SHA-256 `b9942f56bf2b9ace5741218277a93f2c059b42740481cc8a6568bd5540f0617f`).

### Version 45

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v45.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v45.docx) (SHA-256 `c3b5240fa42a22c5fc2c9440ab1302a6d2b6a67b2b0d7fc134c85e4ba5d4696d`).
- Reconstructed draft: [`drafts/article_draft_v45.md`](drafts/article_draft_v45.md) (SHA-256 `a96861d22c65b279287d93e022b431be11de203c947096cfb577a1c3ba1d34aa`).
- Image resources: [`article_resources/v45/`](article_resources/v45/)
  - `Figure_1.png` (SHA-256 `f1c8a2533dbda5b7d025669b0f7efd89026833eecf1f4bd29f6993192fe0ae50`).
  - `Figure_2.png` (SHA-256 `49068cfead55e91871f5470384e368540d2ac277dc616e7ba968547268db42aa`).
  - `Figure_3.png` (SHA-256 `b9942f56bf2b9ace5741218277a93f2c059b42740481cc8a6568bd5540f0617f`).

### Version 46

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v46.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v46.docx) (SHA-256 `d67390c589cb1ff91959ea518c5bb91a6e6ac86f547c2751fb39be834db9f03b`).
- Reconstructed draft: [`drafts/article_draft_v46.md`](drafts/article_draft_v46.md) (SHA-256 `9143921a646fdad7cc2efce8a9c7db602091c6d3c7bec0bd44e16c7f0edb1e69`).
- Image resources: [`article_resources/v46/`](article_resources/v46/)
  - `Figure_1.png` (SHA-256 `f1c8a2533dbda5b7d025669b0f7efd89026833eecf1f4bd29f6993192fe0ae50`).
  - `Figure_2.png` (SHA-256 `49068cfead55e91871f5470384e368540d2ac277dc616e7ba968547268db42aa`).
  - `Figure_3.png` (SHA-256 `b9942f56bf2b9ace5741218277a93f2c059b42740481cc8a6568bd5540f0617f`).

### Version 47

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v47.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v47.docx) (SHA-256 `37bab42fb64c2de4edd1adfca842b985c81ccf2ad572d88c78c5cba66e41f67d`).
- Reconstructed draft: [`drafts/article_draft_v47.md`](drafts/article_draft_v47.md) (SHA-256 `5c3f98dd6b389349640757ad2ff6c3a17dc6c6247c9b1310df9504673df79e30`).
- Correction record (2026-10-17): Restored the affiliations, corresponding-author line, and keywords from the archived DOCX.
- Image resources: [`article_resources/v47/`](article_resources/v47/)
  - `Figure_1.png` (SHA-256 `516309bfe6fa50f56375492054f7d9e6356741e89798cf24b083e95249ae8ee1`).
  - `Figure_2.png` (SHA-256 `5719188fc94fa353498a40d3578e394e9071503de155d6b402d60ef126364040`).
  - `Figure_3.png` (SHA-256 `b6683c20a5a4141c42d1d366a5376f40dcaca582f1fccb831425f01a0044b6e6`).

### Version 48

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v48.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v48.docx) (SHA-256 `103f430fde89afc18dc6495e13c448b53f8325781f0f155ea01011ffcce89cde`).
- Reconstructed draft: [`drafts/article_draft_v48.md`](drafts/article_draft_v48.md) (SHA-256 `1244bebb6a515c3dad8ac1c02001e9f6b62a56620893ae47c407c35350655cab`).
- Image resources: [`article_resources/v48/`](article_resources/v48/)
  - `Figure_1.png` (SHA-256 `7130a1495f268a22fb6611b639a6bb6b3a58ac9fb85b3e128788a17a12c9a1c4`).
  - `Figure_2.png` (SHA-256 `294aabbd48acee6783f1b4336fd301141df33de569c1c69a6a7736b357d24b7e`).
  - `Figure_3.png` (SHA-256 `b6683c20a5a4141c42d1d366a5376f40dcaca582f1fccb831425f01a0044b6e6`).

### Version 49

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v49.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v49.docx) (SHA-256 `ad76dd5dc256229b1e7541f4de745700629c059104123d35d760f8ed46fedac6`).
- Reconstructed draft: [`drafts/article_draft_v49.md`](drafts/article_draft_v49.md) (SHA-256 `67788a5ed49dab5b0939f186481c5df27bc40fa465dbb7b96bc9a20b0ac5d760`).
- Correction record (2026-10-17): Restored the omitted Section 3.4 paragraph from the archived DOCX.
- Image resources: [`article_resources/v49/`](article_resources/v49/)
  - `Figure_0_graphical_abstract.png` (SHA-256 `f4b1c4f9a3889080f1070c743020e1d3fd5de535693b0fb7e80823471772ca5f`).
  - `Figure_1.png` (SHA-256 `d2ce75a7aab75b6a5f335144aa03b661705baa1077d6cfca19d56b89285d43e8`).
  - `Figure_2.png` (SHA-256 `9e20ba8115699b656b29942268f1c6f2efad814942d0486e67cd963198f612ae`).
  - `Figure_3.png` (SHA-256 `e3057fe463dc338e221e671106f56bc93fbc1f5de75645cf107a1b4a9fb78ee1`).
  - `Figure_4.png` (SHA-256 `7130a1495f268a22fb6611b639a6bb6b3a58ac9fb85b3e128788a17a12c9a1c4`).

### Version 52

- Source DOCX: [`manuscript_versions/Electrochimica_Acta_research_article_draft_v52.docx`](manuscript_versions/Electrochimica_Acta_research_article_draft_v52.docx) (SHA-256 `1d301cb3d5c663fac0b67630bc8a75b97bab54a06321b67ddb795f3d555a5e0b`).
- Reconstructed draft: [`drafts/article_draft_v52.md`](drafts/article_draft_v52.md) (SHA-256 `e28312c222ec3a82225eca6845e49cebcac2199ca902afa0a16453a72ef17aa3`).
- Image resources: [`article_resources/v52/`](article_resources/v52/)
  - `Figure_0_graphical_abstract.png` (SHA-256 `bcd2b736a1865d7576fece29e34d257ca2e9d1ee3ab484992871488b94bbc248`).
  - `Figure_1.png` (SHA-256 `2486bb2cc01f24c7884cf68df3dd52184f81923612e761612a0ebb8874b9ce58`).
  - `Figure_2.png` (SHA-256 `4d2c53ca13919af6fd3386d50aa51b2da91c14e5a8d11655496e015e3c40b5ac`).
  - `Figure_3.png` (SHA-256 `e932276fc28494d4a7c5920cf1886bbdbcf012b92b71ba8c74ca2cb530eb62ff`).
  - `Figure_4.png` (SHA-256 `4c76ef5b96765e67776b51d6f07f631b85f0471a6db3ec29b251ec8a4e8d778d`).
- Full-DOCX review record: [`reviews/review_v52.md`](reviews/review_v52.md) (SHA-256 `95ae283b42e3123e9d705e7cf47ca58a56939973d262f6bb2f9eea2d8150e439`); includes the complete text, 89 tracked insertions, 84 tracked deletions, and no Word comments.
