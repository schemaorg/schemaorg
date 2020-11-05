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

function _createForOfIteratorHelper(o, allowArrayLike) { var it; if (typeof Symbol === "undefined" || o[Symbol.iterator] == null) { if (Array.isArray(o) || (it = _unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = o[Symbol.iterator](); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it.return != null) it.return(); } finally { if (didErr) throw err; } } }; }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }

function _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err); } _next(undefined); }); }; }

var data = "\n            {\n              \"@context\": \"https://schema.org\",\n              \"@graph\": [\n                {\n                  \"@id\": \"#author\",\n                  \"@type\": \"Person\",\n                  \"birthDate\": \"1892\",\n                  \"deathDate\": \"1973\",\n                  \"name\": \"Tolkien, J. R. R. (John Ronald Reuel)\",\n                  \"sameAs\": \"http://viaf.org/viaf/95218067\"\n                },\n                {\n                  \"@id\": \"#trilogy\",\n                  \"@type\": \"Book\",\n                  \"about\": \"http://id.worldcat.org/fast/1020337\",\n                  \"hasPart\": [\n                    {\n                      \"@id\": \"#book3\",\n                      \"@type\": [\n                        \"Book\",\n                        \"PublicationVolume\"\n                      ],\n                      \"name\": \"The Return of the King\",\n                      \"about\": \"http://id.worldcat.org/fast/1020337\",\n                      \"isPartOf\": \"#trilogy\",\n \"inLanguage\": \"en\",\n" +
    "                      \"volumeNumber\": \"3\",\n                      \"author\": \"#author\"\n                    },\n                    {\n                      \"@id\": \"#book2\",\n                      \"@type\": [\n                          \"Book\",\n                          \"PublicationVolume\"\n                      ],\n                      \"name\": \"The Two Towers\",\n                      \"about\": \"http://id.worldcat.org/fast/1020337\",\n                      \"isPartOf\": \"#trilogy\",\n                      \"inLanguage\": \"en\",\n                      \"volumeNumber\": \"2\",\n                      \"author\": \"#author\"\n                    },\n                    {\n                      \"@id\": \"#book1\",\n                      \"@type\": [\n                        \"Book\",\n                        \"PublicationVolume\"\n                      ],\n                      \"name\": \"The Fellowship of the Ring\",\n                      \"about\": \"http://id.worldcat.org/fast/1020337\",\n                      \"isPartOf\": \"#trilogy\",\n   "+
    "                   \"inLanguage\": \"en\",\n                      \"volumeNumber\": \"1\",\n                      \"author\": \"#author\"\n                    }\n                  ],\n                  \"name\": \"Lord of the Rings\",\n                  \"inLanguage\": \"en\",\n                  \"genre\": \"fictional\",\n                  \"author\": \"#author\"\n                }\n              ]\n            }\n            ";


function prettyMarkup(_x) {
    return _prettyMarkup.apply(this, arguments);
}

function _prettyMarkup() {
    _prettyMarkup = _asyncToGenerator( /*#__PURE__*/regeneratorRuntime.mark(function _callee(data) {
        var prettyMarkupTextarea, prettyMarkupDiv, elements, _iterator, _step, el;

        return regeneratorRuntime.wrap(function _callee$(_context) {
            while (1) {
                switch (_context.prev = _context.next) {
                    case 0:
                        prettyMarkupTextarea = document.getElementById('text-pretty-markup');
                        _context.next = 3;
                        return prettyMarkupText(data);

                    case 3:
                        prettyMarkupTextarea.value = _context.sent;
                        prettyMarkupDiv = document.getElementById('pretty-markup');
                        _context.next = 7;
                        return prettyMarkupHtml(data);

                    case 7:
                        elements = _context.sent;
                        _iterator = _createForOfIteratorHelper(elements);

                        try {
                            for (_iterator.s(); !(_step = _iterator.n()).done;) {
                                el = _step.value;
                                prettyMarkupDiv.appendChild(el);
                            }
                        } catch (err) {
                            _iterator.e(err);
                        } finally {
                            _iterator.f();
                        }

                    case 10:
                    case "end":
                        return _context.stop();
                }
            }
        }, _callee);
    }));
    return _prettyMarkup.apply(this, arguments);
}

prettyMarkup(data);