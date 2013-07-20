import sys, zipfile, os, shutil, os.path
from PIL import Image

filename = sys.argv[1]

if filename[-5:] != ".epub" or len(sys.argv) != 2:
	print "Usage: %s <epub file>" % sys.argv[0]
	sys.exit(1)

imgDir = os.path.join(os.path.dirname(filename), "%s_images" % os.path.basename(filename)[:-5])
if not os.path.exists(imgDir): os.mkdir(imgDir)

# custom css
css = """
html * {
		font-size: %s !important;
		color: %s !important;
		font-family: %s !important;
	}
"""
customCss = css % ("1em", "#000", "Arial")

with zipfile.ZipFile(filename, 'r') as zipper:
	for mem in [f if "html" in f else None for f in zipper.namelist()]:
		if mem:
			# set parent directory
			global parDir
			parDir = os.path.split(mem)[0]

			# extract html file
			print "Extracting %s" % mem
			zipper.extract(mem)

			# apply custom css to html
			#print "> Applying custom css"
			#f = open(mem, "r+")
			#cont = f.read()
			#newCont = cont.replace('<style type="text/css">', '<style type="text/css">%s' % customCss)
			#f.write(newCont)
			#f.close()

			# render html file to image
			imgName =  "%s.png" % os.path.basename(mem).split(".")[0]
			imgFile = os.path.join(imgDir, imgName)
			print "> Saving image to %s" % imgFile
			os.system("python2 grabHtml.py -o %s %s" % (imgFile, mem))

			# crop image to correct size
			print ">> Resizing image"
			img = Image.open(imgFile)
			# set width to 600
			img.thumbnail((600, 800000), Image.ANTIALIAS) # some huge height in order to get a width of 600 -> think of better solution
			# split into 600x800 chunks
			c = 1
			for i in [i if i % 800 == 0 else None for i in range(0, img.size[1] + 1)]:
				if i != None:
					print ">>> Offset: %i" % i
					chunk = img.crop((0, i, 600, i + 800))
					chunkName = "%s_%i.png" % (imgName.split(".")[0], c)
					chunkFile = os.path.join(imgDir, chunkName)
					chunk.save(chunkFile, "PNG")
					c += 1

			# remove undeeded image
			print "> Deleting %s" % imgFile
			os.remove(imgFile)


print "Deleting %s" % parDir
shutil.rmtree(parDir)
