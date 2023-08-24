import gulp from 'gulp'
import inject from 'gulp-inject-file'
import htmlmin from 'gulp-htmlmin'
import del from 'del'

/* Cleanup task */
export function cleanup(){
	return del(['common'])
}

/* Layout builder task */
export function buildLayout(){
	return gulp.src( [ 'src/views/**/*.html' ] )
		.pipe(inject({ pattern: '<!--inject:<filename>-->' }))
		.pipe(htmlmin({ collapseWhitespace: true }))
		.pipe( gulp.dest( './' ) )
}

/* Watch task */
export function watch(){
	gulp.watch( 'src/**/*.html', buildLayout )
}

/* Default task */
export default gulp.series(buildLayout, cleanup)
