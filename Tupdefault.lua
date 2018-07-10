blender = 'export PYTHONDONTWRITEBYTECODE=1; blender '
export_escn = blender .. ' -b --python $(TOP)/import_stl.py -- '

tup.creategitignore()

tup.foreach_rule('*.stl', export_escn .. '--infile %f --outfile %o', '%B.blend')
tup.foreach_rule('*.STL', export_escn .. '--infile %f --outfile %o', '%B.blend')
