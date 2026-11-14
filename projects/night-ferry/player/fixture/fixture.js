/* Night Ferry — bundled FIXTURE for checking the player.
 *
 * This is placeholder text, not the real case. It exists so the page can be
 * opened with no case files (including from file://, where browsers refuse to
 * fetch sibling JSON). The truth sheet and each scene below use exactly the
 * case schema; only this small wrapper differs, because a classic script can
 * carry the objects where fetch() cannot.
 */
window.NIGHT_FERRY_FIXTURE = {
  label: 'Bundled fixture — placeholder text, not story content',
  truth: {
    case: 'fixture-night-ferry',
    title: 'FIXTURE — The Blue Lamp (not story content)',
    facts: [
      { id: 'F1', statement: 'FIXTURE: The blue lamp stood on the cargo crate beside the loading ramp before departure.' },
      { id: 'F2', statement: 'FIXTURE: The winch lifted the cargo crate from the ramp to the deck at 21:10.' },
      { id: 'F3', statement: 'FIXTURE: The engine-room log records the winch motor running once, at 21:10.' },
      { id: 'F4', statement: 'FIXTURE: After 21:10 the shore account saw the blue lamp on the deck, not on the ramp.' },
      { id: 'F5', statement: 'FIXTURE: The lamp glass carried fresh paw prints.' },
      { id: 'F6', statement: 'FIXTURE: The cat was the only creature on the crate at 21:10.' }
    ],
    deduction: {
      question: 'FIXTURE QUESTION: How did the blue lamp get from the ramp to the deck?',
      answer: 'FIXTURE ANSWER: The cat was riding the crate when the winch lifted it, so the lamp travelled up with the crate and the cat.'
    },
    scenes: [
      { id: 'landing-clerk', file: 'landing-clerk.json', title: 'FIXTURE — The shore account' },
      { id: 'engine-room', file: 'engine-room.json', title: 'FIXTURE — The engine-room account' }
    ]
  },
  scenes: {
    'landing-clerk': {
      id: 'landing-clerk',
      title: 'FIXTURE — The shore account',
      perspective: 'shore',
      paragraphs: [
        'FIXTURE — This paragraph is placeholder prose. The blue lamp waited on the cargo crate at the foot of the ramp while the last passengers came aboard.',
        'FIXTURE — This paragraph is placeholder prose. At 21:10 the winch lifted the crate; afterwards I saw the lamp standing on the deck, and its glass was marked with paw prints.'
      ],
      statements: [
        { fact: 'F1', text: 'FIXTURE: The blue lamp was on the crate at the foot of the ramp.' },
        { fact: 'F2', text: 'FIXTURE: The winch lifted the crate at 21:10.' },
        { fact: 'F4', text: 'FIXTURE: After the lift, the lamp stood on the deck.' },
        { fact: 'F5', text: 'FIXTURE: The lamp glass had fresh paw prints.' }
      ]
    },
    'engine-room': {
      id: 'engine-room',
      title: 'FIXTURE — The engine-room account',
      perspective: 'engine',
      paragraphs: [
        'FIXTURE — This paragraph is placeholder prose. I was at the winch panel when the motor started; the log shows exactly one lift, at 21:10.',
        'FIXTURE — This paragraph is placeholder prose. Through the grating I saw the cat sitting on the crate just as the winch took the weight.'
      ],
      statements: [
        { fact: 'F3', text: 'FIXTURE: The winch motor ran once, at 21:10.' },
        { fact: 'F6', text: 'FIXTURE: The cat was on the crate when the winch started.' },
        { fact: 'F1', text: 'FIXTURE: The blue lamp stood on the crate below the grating.' }
      ]
    }
  }
};
