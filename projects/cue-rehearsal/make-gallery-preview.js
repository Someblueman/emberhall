#!/usr/bin/env node
'use strict';

const model = require('./model.js');

const sampleRehearsal = model.editStep(model.initial(), 'tables', { duration: 14 });
process.stdout.write(model.previewSvg(sampleRehearsal));
