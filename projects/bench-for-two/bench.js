'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const radios = [...document.querySelectorAll('input[name="recipient"]')];
  let recipient = null;
  let opened = false;
  const closedDescription = $('bench-desc').textContent;
  function render() {
    $('unfold').disabled = recipient === null;
    $('placement').textContent = recipient ? `“For you.” is in ${recipient === 'edie' ? 'Edie’s' : 'Nell’s'} envelope.` : 'The words are still on the bench.';
    radios.forEach(radio => { radio.checked = radio.value === recipient; });
    $('letters').hidden = !opened;
    if (!recipient) return;
    const letters = BenchLetter.divide(recipient);
    for (const name of ['edie', 'nell']) {
      $(name+'-letter').replaceChildren(...letters[name].map(line => {
        const p = document.createElement('p');
        p.textContent = line.text;
        if (line.loose) p.className = 'loose';
        return p;
      }));
    }
    $('other-name').textContent = recipient === 'edie' ? 'Nell' : 'Edie';
  }
  $('lift').addEventListener('click', () => {
    $('closed').hidden = true;
    document.querySelector('.stage').classList.add('is-open');
    $('bench-desc').textContent = 'The bench lid is raised. A sheet of paper lies in the dark compartment. Two envelopes wait on the floor.';
    $('desk').hidden = false;
    $('desk-heading').focus();
  });
  radios.forEach(radio => radio.addEventListener('change', () => { recipient = radio.value; render(); }));
  $('unfold').addEventListener('click', () => {
    opened = true;
    render();
    $('letters-heading').focus();
  });
  $('move').addEventListener('click', () => {
    recipient = recipient === 'edie' ? 'nell' : 'edie';
    render();
    $('letters-heading').focus();
  });
  $('fold').addEventListener('click', () => {
    opened = false;
    render();
    radios.find(radio => radio.checked).focus();
  });
  $('reset').addEventListener('click', () => {
    recipient = null;
    opened = false;
    render();
    $('paper').parentElement.open = false;
    $('desk').hidden = true;
    $('closed').hidden = false;
    document.querySelector('.stage').classList.remove('is-open');
    $('bench-desc').textContent = closedDescription;
    $('lift').focus();
  });
  $('paper').replaceChildren(...BenchLetter.paper.map(line => {
    const li = document.createElement('li');
    const name = document.createElement('small');
    name.textContent = line.to ? (line.to === 'edie' ? 'Edie' : 'Nell') : 'Loose';
    li.append(name, document.createTextNode(' '+line.text));
    return li;
  }));
  render();
})();
