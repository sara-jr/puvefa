const { src, dest, series } = require('gulp');
const uglify = require('gulp-uglify');
const concat = require('gulp-concat');

const DEST = 'pdv/static/pdv/'


function build_js(){
  return src([
    'node_modules/beercss/dist/cdn/beer.min.js',
    'node_modules/htmx.org/dist/htmx.js',
    'node_modules/htmx.org/dist/ext/response-targets.js',
    'node_modules/alpinejs/dist/cdn.min.js',
    'node_modules/currency.js/dist/currency.min.js',
  ])
    .pipe(dest(DEST))
}


function pass_css(){
  return src([
    'node_modules/beercss/dist/cdn/beer.min.css',
    'node_modules/beercss/dist/cdn/*.woff2',
  ])
    .pipe(dest(DEST));
}


exports.default = series(
  pass_css,
  build_js
);
