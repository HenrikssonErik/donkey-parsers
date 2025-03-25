show_commands:
	grep -E '^[a-zA-Z0-9_-]+:' Makefile | sed 's/://' \

atlas_h1_benign:
	test -f venv/bin/activate || virtualenv -p $(shell which python) venv
	. venv/bin/activate ; \
		python atlas_parser.py \
			-d ../../../data/atlasv2/data/benign/h1/cbc-edr \
			-i edr-h1-benign.jsonl \
			-b base/atlas-base-h1-benign.txt \
			-s stream/atlas-stream-h1-benign.txt \

atlas_h2_benign:
	test -f venv/bin/activate || virtualenv -p $(shell which python) venv
	. venv/bin/activate ; \
		python atlas_parser.py \
			-d ../../../data/atlasv2/data/benign/h2/cbc-edr \
			-i edr-h2-benign.jsonl \
			-b base/atlas-base-h2-benign.txt \
			-s stream/atlas-stream-h2-benign.txt \

atlas_h1_multi_attack:
	test -f venv/bin/activate || virtualenv -p $(shell which python) venv

	number=1 ; while [ $$number -le 6 ] ; do \
		venv/bin/python atlas_parser.py \
			-d ../../../data/atlasv2/data/attack/h1/cbc-edr \
			-i edr-h1-m$$number.jsonl \
			-b base/atlas-base-h1-attack-m$$number.txt \
			-s stream/atlas-stream-h1-attack-m$$number.txt ; \
		number=`expr $$number + 1` ; \
	done 

atlas_h2_multi_attack:
	test -f venv/bin/activate || virtualenv -p $(shell which python) venv
	
	number=1 ; while [ $$number -le 6 ] ; do \
		venv/bin/python atlas_parser.py \
			-d ../../../data/atlasv2/data/attack/h2/cbc-edr \
			-i edr-h2-m$$number.jsonl \
			-b base/atlas-base-h2-attack-m$$number.txt \
			-s stream/atlas-stream-h2-attack-m$$number.txt ; \
		number=`expr $$number + 1` ; \
	done

atlas_h1_single_attack:
	test -f venv/bin/activate || virtualenv -p $(shell which python) venv

	number=1 ; while [ $$number -le 4 ] ; do \
		venv/bin/python atlas_parser.py \
			-d ../../../data/atlasv2/data/attack/h1/cbc-edr \
			-i edr-h1-s$$number.jsonl \
			-b base/atlas-base-h1-attack-s$$number.txt \
			-s stream/atlas-stream-h1-attack-s$$number.txt ; \
		number=`expr $$number + 1` ; \
	done 

clean:
	rm -f ../../../data/atlasv2/data/benign/h1/cbc-edr/base ../../../data/atlasv2/data/benign/h1/cbc-edr/stream
	rm -rf venv
