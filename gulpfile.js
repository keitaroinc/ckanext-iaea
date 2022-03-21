const path = require("path");
const { src, watch, dest, parallel } = require("gulp");
const less = require("gulp-less");
const if_ = require("gulp-if");
const sourcemaps = require("gulp-sourcemaps");
const rename = require("gulp-rename");

const with_sourcemaps = () => !!process.env.DEBUG;
const renamer = (path) => {
  const variant = process.argv[3];
  if (variant) {
    // convert main/main-rtl into green/green-rtl
    path.basename = path.basename.replace("main", variant.slice(2));
  }
  return path;
};

const build = () =>
  src([
    __dirname + "/ckanext/iaea/public/base/less/main.less",
    __dirname + "/ckanext/iaea/public/base/less/main-rtl.less",
  ])
    .pipe(if_(with_sourcemaps(), sourcemaps.init()))
    .pipe(less())
    .pipe(if_(with_sourcemaps(), sourcemaps.write()))
    .pipe(rename(renamer))
    .pipe(dest(__dirname + "/ckanext/iaea/fanstatic/css"));
const watchSource = () =>
  watch(
    __dirname + "/ckanext/iaea/public/base/less/**/*.less",
    { ignoreInitial: false },
    build
  );

  exports.build = build;
  exports.watch = watchSource;