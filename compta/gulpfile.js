var gulp = require('gulp');
var uglify = require('gulp-uglify');
var sourcemaps = require('gulp-sourcemaps');
var browserify = require('browserify');
var del = require('del');
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');

var paths = {
    js: {
        index: 'index.js',
        generated_path: 'static/js/'
    }
};

gulp.task('clean', function() {
    del(paths.js.generated_path + '*');
});

gulp.task('js', ['clean'], function() {
    browserify(paths.js.index, { debug: true }).bundle()
        .pipe(source('bundle.js'))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(uglify())
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(paths.js.generated_path));
});

// Rerun tasks whenever a file changes.
gulp.task('watch', function() {
    gulp.watch(paths.js.index, ['js']);
});

gulp.task('default', ['clean', 'watch', 'js']);
