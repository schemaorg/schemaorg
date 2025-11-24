/**
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
"use strict";

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _iterableToArrayLimit(arr, i) { if (typeof Symbol === "undefined" || !(Symbol.iterator in Object(arr))) return; var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

function _createForOfIteratorHelper(o, allowArrayLike) { var it; if (typeof Symbol === "undefined" || o[Symbol.iterator] == null) { if (Array.isArray(o) || (it = _unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = o[Symbol.iterator](); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it.return != null) it.return(); } finally { if (didErr) throw err; } } }; }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

var TYPE_URI = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type';
var NAME_URI = 'http://schema.org/name';
var defaultBase = 'http://example.org/';
var htmlIndentStep = 30; // one indentation step in HTML representation (in px)

var textIndentStep = 4; // one indentation step in text representation (in spaces)

/**
 * @param {string} text
 * @return {string}
 */

function replacePrefix(text) {
    text = text.split(/https?:\/\/schema.org\//g).join('');
    text = text.split(/http:\/\/www.w3.org\/1999\/02\/22-rdf-syntax-ns#/g).join('@');
    text = text.split(/http:\/\/www.w3.org\/2000\/01\/rdf-schema#/g).join('@');
    return text;
}
/**
 * Does a random permutation of array elements
 * @param array
 */


function shuffleArray(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}
/**
 * @param {Map<string, *>} shapes
 * @return {number[]}
 */


function makeColorSet(shapes) {
    var totalEntitiesCount = 0;
    var colors = [];

    var _iterator = _createForOfIteratorHelper(shapes.values()),
        _step;

    try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
            var store = _step.value;
            totalEntitiesCount += new Set(store.getSubjects().map(function (x) {
                return x.id;
            })).size;
        }
    } catch (err) {
        _iterator.e(err);
    } finally {
        _iterator.f();
    }

    for (var i = 0; i < totalEntitiesCount; i++) {
        colors.push(i / totalEntitiesCount * 360);
    }

    shuffleArray(colors);
    return colors;
}
/**
 * Makes a text layout for a single triple
 * @param {string} subject
 * @param {string} predicate
 * @param {string} object
 * @param {{
 *     indentLevel: number,
 *     entityColorId: number,
 *     isTarget: boolean
 * }} options
 * @return {string}
 */


function dataItemLayoutText(subject, predicate, object, options) {
    var indent = ' '.repeat(options.indentLevel * textIndentStep);
    var objectText = object;
    // If there is a language tag, prefix it.
    if (options.language) {
        objectText = '@' + options.language + ' ' + objectText;
    }
    return "".concat(indent).concat(replacePrefix(predicate), ": ").concat(replacePrefix(objectText));
}
/**
 * Makes an html layout for a single triple
 * @param {string} subject
 * @param {string} predicate
 * @param {string} object
 * @param {{
 *     indentLevel: number,
 *     entityColorId: number,
 *     isTarget: boolean,
 * }} options
 * @return {*}
 */


function dataItemLayoutHtml(subject, predicate, object, options) {
    var indentBlock = document.createElement('div');
    indentBlock.style.width = "".concat(options.indentLevel * htmlIndentStep, "px");
    indentBlock.style.borderRight = "3px solid hsl(".concat(options.entityColorId, ", 60%, 70%)");
    indentBlock.style.marginRight = '3px';
    var predicateEl = document.createElement('div');
    predicateEl.classList.add('predicate');
    var predicateTextEl = document.createElement('div');
    predicateTextEl.innerText = replacePrefix(predicate);
    predicateEl.appendChild(indentBlock);
    predicateEl.appendChild(predicateTextEl);
    var objectEl = document.createElement('div');
    objectEl.classList.add('object');

    if (options.language) {
      var langSpan = document.createElement('span');
      langSpan.innerText = '@' + options.language + ' ';
      langSpan.classList.add('language-tag');
      objectEl.appendChild(langSpan);
    }

    var valueSpan = document.createElement('span');
    valueSpan.innerText = object;
    objectEl.appendChild(valueSpan);
    var tripleRow = document.createElement('div');
    tripleRow.classList.add('triple-row');
    tripleRow.style.background = options.isTarget ? '#f4f4f4' : '#fff';
    tripleRow.appendChild(predicateEl);
    tripleRow.appendChild(objectEl);
    return tripleRow;
}
/**
 * Recursive level-based html generation
 * @param store - n3 store with quads
 * @param {string} id - current node identifier
 * @param {string[]} displayed
 * @param {number} indentLevel - current indentation level
 * @param {function} layoutGenerator
 * @param {{
 *  target?:{type: 'entity'|'property', uri: string},
 *  colorSet?: number[]
 *  }|undefined} options
 * @return {HTMLElement[]}
 */


function markupLevel(store, id, displayed, indentLevel, layoutGenerator) {
    var _levelQuads, _levelQuads2;

    var options = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : undefined;
    if (displayed.includes(id)) return [];
    displayed.push(id);
    var levelQuads = store.getQuads(id, undefined, undefined);
    if (levelQuads.length === 0) return [];
    var tripleRows = []; // options for dataItemLayout building

    var layoutOptions = {
        indentLevel: indentLevel,
        entityColorId: options && options.colorSet ? options.colorSet.pop() : Math.random() * 360,
        isTarget: false
    }; // important properties (type & name) go first

    var typeQuad = store.getQuads(id, TYPE_URI, undefined);
    var nameQuad = store.getQuads(id, NAME_URI, undefined);
    levelQuads = levelQuads.filter(function (x) {
        return x.predicate.value !== TYPE_URI && x.predicate.value !== NAME_URI;
    });

    (_levelQuads = levelQuads).push.apply(_levelQuads, _toConsumableArray(nameQuad));

    (_levelQuads2 = levelQuads).push.apply(_levelQuads2, _toConsumableArray(typeQuad));

    levelQuads.reverse(); // adding @id (it's not in quads)

    if (levelQuads.length > 0 && levelQuads[0].subject.termType === 'NamedNode') {
        tripleRows.push(layoutGenerator(id, '@id', id, layoutOptions));
    }

    var _iterator2 = _createForOfIteratorHelper(levelQuads),
        _step2;

    try {
        for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
            var quad = _step2.value;
            // used for highlighting target triples
            layoutOptions.isTarget = options && options.target && (options.target.type === 'entity' && typeQuad.length > 0 && typeQuad[0].object.value === options.target.uri || options.target.type === 'property' && quad.predicate.value === options.target.uri);
            layoutOptions.language = quad.object.language;
            var next_level = markupLevel(store, quad.object.id, displayed, indentLevel + 1, layoutGenerator, options);

            if (next_level.length > 0) {
                tripleRows.push(layoutGenerator(id, quad.predicate.value, '', layoutOptions));
                tripleRows.push.apply(tripleRows, _toConsumableArray(next_level));
            } else {
                var object = quad.object.termType === 'NamedNode' ? replacePrefix(quad.object.value) : quad.object.value;
                tripleRows.push(layoutGenerator(id, quad.predicate.value, object, layoutOptions));
            }
        }
    } catch (err) {
        _iterator2.e(err);
    } finally {
        _iterator2.f();
    }

    return tripleRows;
}
/**
 * Get as close as possible base url that is still valid
 * @param {string} data - input markup
 * @return {string}
 */


function makeBaseUrl(data) {
    var dataObj;

    try {
        dataObj = JSON.parse(data);
    } catch (e) {
        // return default if can't be parsed as JSON
        return defaultBase;
    }

    if (dataObj.hasOwnProperty('@id')) {
        // if has an @id and @id has a full url prefix (e.g. https://, etc.), return it
        // else this is a relative url and we need to add the default base to it
        if (dataObj['@id'].match(/.*?:\/\/.*/g)) return dataObj['@id'];else return defaultBase + dataObj['@id'];
    }

    return defaultBase;
}
/**
 * Gets data from <script> tags
 * @param {string} data
 * @return {string|*}
 */


function removeScript(data) {
    try {
        JSON.parse(data);
        return data;
    } catch (e) {
        var domParser = new DOMParser();
        var jsonld = [].slice.call(domParser.parseFromString(data, 'text/html').getElementsByTagName('script')).filter(function (x) {
            return x.type === 'application/ld+json';
        }); // if there is exactly one json-ld, then parse it, else throw an exception
        // (I assume that only one json-ld can be in the example, but if not we still can
        // parse and display more than one)

        if (jsonld.length === 1) return jsonld[0].innerText;else if (jsonld.length > 1) throw 'not single json-ld in the example';
    }
}
/**
 * Base function that will can be called for pretty markup generation
 * @param {string} data - json-ld markup
 * @param {{baseUrl?: string, target?: {type: 'entity'|'property', uri: string}}|undefined} options
 *  - used for highlighting target entities/properties, e.g. startDate in the Event entity
 * @return {Promise<HTMLElement[]>}
 */


function prettyMarkupHtml(_x) {
    return _prettyMarkupHtml.apply(this, arguments);
}
/**
 * Base function that will can be called for pretty markup generation
 * @param {string} data - json-ld markup
 * @param {{baseUrl?: string, target?: {type: 'entity'|'property', uri: string}}|undefined} options
 *  - used for highlighting target entities/properties, e.g. startDate in the Event entity
 * @return {Promise<string>}
 */


function _prettyMarkupHtml() {
    _prettyMarkupHtml = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(data) {
        var options,
            baseUrl,
            target,
            shapes,
            colorSet,
            tripleRows,
            _iterator3,
            _step3,
            _step3$value,
            id,
            shape,
            _args = arguments;

        return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
                switch (_context.prev = _context.next) {
                    case 0:
                        options = _args.length > 1 && _args[1] !== undefined ? _args[1] : undefined;
                        data = removeScript(data); // passed baseUrl is prioritised, but if not given, a close to the markup baseUrl will be used

                        baseUrl = options && options.baseUrl ? options.baseUrl : makeBaseUrl(data);
                        target = options && options.target ? options.target : undefined;
                        _context.t0 = schemarama;
                        _context.next = 7;
                        return schemarama.stringToQuads(data, baseUrl);

                    case 7:
                        _context.t1 = _context.sent;
                        shapes = _context.t0.quadsToShapes.call(_context.t0, _context.t1);
                        colorSet = makeColorSet(shapes);
                        tripleRows = [];
                        _iterator3 = _createForOfIteratorHelper(shapes.entries());

                        try {
                            for (_iterator3.s(); !(_step3 = _iterator3.n()).done;) {
                                _step3$value = _slicedToArray(_step3.value, 2), id = _step3$value[0], shape = _step3$value[1];
                                tripleRows.push.apply(tripleRows, _toConsumableArray(markupLevel(shape, id, [], 0, dataItemLayoutHtml, {
                                    colorSet: colorSet,
                                    target: target
                                })));
                            }
                        } catch (err) {
                            _iterator3.e(err);
                        } finally {
                            _iterator3.f();
                        }

                        return _context.abrupt("return", tripleRows);

                    case 14:
                    case "end":
                        return _context.stop();
                }
            }
        }, _callee);
    }));
    return _prettyMarkupHtml.apply(this, arguments);
}

function prettyMarkupText(_x2) {
    return _prettyMarkupText.apply(this, arguments);
}

function _prettyMarkupText() {
    _prettyMarkupText = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee2(data) {
        var options,
            baseUrl,
            target,
            shapes,
            colorSet,
            tripleRows,
            _iterator4,
            _step4,
            _step4$value,
            id,
            shape,
            _args2 = arguments;

        return regeneratorRuntime.wrap(function _callee2$(_context2) {
            while (1) {
                switch (_context2.prev = _context2.next) {
                    case 0:
                        options = _args2.length > 1 && _args2[1] !== undefined ? _args2[1] : undefined;
                        data = removeScript(data); // passed baseUrl is prioritised, but if not given, a close to the markup baseUrl will be used

                        baseUrl = options && options.baseUrl ? options.baseUrl : makeBaseUrl(data);
                        target = options && options.target ? options.target : undefined;
                        _context2.t0 = schemarama;
                        _context2.next = 7;
                        return schemarama.stringToQuads(data, baseUrl);

                    case 7:
                        _context2.t1 = _context2.sent;
                        shapes = _context2.t0.quadsToShapes.call(_context2.t0, _context2.t1);
                        colorSet = makeColorSet(shapes);
                        tripleRows = [];
                        _iterator4 = _createForOfIteratorHelper(shapes.entries());

                        try {
                            for (_iterator4.s(); !(_step4 = _iterator4.n()).done;) {
                                _step4$value = _slicedToArray(_step4.value, 2), id = _step4$value[0], shape = _step4$value[1];
                                tripleRows.push(markupLevel(shape, id, [], 0, dataItemLayoutText, {
                                    colorSet: colorSet,
                                    target: target
                                }).join('\n'));
                            }
                        } catch (err) {
                            _iterator4.e(err);
                        } finally {
                            _iterator4.f();
                        }

                        return _context2.abrupt("return", tripleRows.join('\n\n'));

                    case 14:
                    case "end":
                        return _context2.stop();
                }
            }
        }, _callee2);
    }));
    return _prettyMarkupText.apply(this, arguments);
}