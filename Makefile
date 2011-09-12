.PHONY: lint deploy clean wc pep8 pyflakes

lint: pep8 pyflakes

deploy:
	fab live deploy

clean:
	rm -fr lastpage-*-deploy.tar.bz2
	find . -name '*~' -o -name '*.pyc' -print0 | xargs -0 -r rm

wc:
	find . -name '*.py' -print0 | xargs -0 wc -l

pep8:
	find . -name '*.py' -print0 | xargs -0 -n 1 pep8 --repeat

pyflakes:
	find . -name '*.py' -print0 | xargs -0 pyflakes
