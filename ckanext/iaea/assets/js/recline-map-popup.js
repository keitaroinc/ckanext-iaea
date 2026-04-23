(function () {
  'use strict';

  // Patch L.Layer.prototype.bindPopup so every marker popup gets maxHeight: 200,
  // overriding the bare bindPopup calls in core recline.js without touching core files.
  function patch() {
    if (typeof L === 'undefined' || !L.Layer || !L.Layer.prototype.bindPopup) {
      setTimeout(patch, 50);
      return;
    }

    var _orig = L.Layer.prototype.bindPopup;
    L.Layer.prototype.bindPopup = function (content, options) {
      if (!options) {
        options = { maxHeight: 200 };
      } else if (!options.maxHeight) {
        options.maxHeight = 200;
      }
      return _orig.call(this, content, options);
    };
  }

  patch();
}());
