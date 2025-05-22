show_commands:
	grep -E '^[a-zA-Z0-9_-]+:' Makefile | sed 's/://' \

make_all:
	make atlas_h1_benign
	make atlas_h2_benign
	make atlas_h1_benign_split
	make atlas_h2_benign_split

	make atlas_h1_multi_attack
	make atlas_h2_multi_attack
	make atlas_h1_single_attack


#-------------------------------------------------------------#
#---------------------------BENIGN----------------------------#
#-------------------------------------------------------------#

atlas_h1_benign:
	test -f venv/bin/activate || virtualenv -p $(shell which python) venv
	. venv/bin/activate ; \
		python atlas_parser.py \
			-d ../../../data/atlasv2/data/benign/h1/cbc-edr \
			-i edr-h1-benign.jsonl \
			-b base/atlas-base-h1-benign.txt \
			-s stream/atlas-stream-h1-benign.txt \


splitter_atlas_h1_benign:
	mkdir -p split_base
	mkdir -p split_stream
	test -f venv/bin/activate || virtualenv -p $(shell which python) venv
	. venv/bin/activate ; \
		python atlas_splitter.py \
			-d ../../../data/atlasv2/data/benign/h1/cbc-edr \
			-i edr-h1-benign \
			-b split_base/atlas-base-h1-benign \
			-s split_stream/atlas-stream-h1-benign \
			-f 8 \

atlas_h2_benign:
	test -f venv/bin/activate || virtualenv -p $(shell which python) venv
	. venv/bin/activate ; \
		python atlas_parser.py \
			-d ../../../data/atlasv2/data/benign/h2/cbc-edr \
			-i edr-h2-benign.jsonl \
			-b base/atlas-base-h2-benign.txt \
			-s stream/atlas-stream-h2-benign.txt \

splitter_atlas_benign:
	mkdir -p ../../../data/atlasv2/data/benign/h1/cbc-edr/split_base
	mkdir -p ../../../data/atlasv2/data/benign/h1/cbc-edr/split_stream
	mkdir -p ../../../data/atlasv2/data/benign/h2/cbc-edr/split_base
	mkdir -p ../../../data/atlasv2/data/benign/h2/cbc-edr/split_stream

	test -f venv/bin/activate || virtualenv -p $(shell which python) venv

	number=1 ; while [ $$number -le 2 ] ; do \
		venv/bin/python atlas_splitter.py \
			-d ../../../data/atlasv2/data/benign/h$$number/cbc-edr \
			-i edr-h$$number-benign \
			-b split_base/atlas-base-h$$number-benign \
			-s split_stream/atlas-stream-h$$number-benign \
			-f 8 ; \
		number=`expr $$number + 1` ; \
	done 
			

#-------------------------------------------------------------#
#---------------------------ATTACKS---------------------------#
#-------------------------------------------------------------#
splitter_atlas_attack:
	mkdir -p ../../../data/atlasv2/data/attack/h1/cbc-edr/split_base
	mkdir -p ../../../data/atlasv2/data/attack/h1/cbc-edr/split_stream
	mkdir -p ../../../data/atlasv2/data/attack/h2/cbc-edr/split_base
	mkdir -p ../../../data/atlasv2/data/attack/h2/cbc-edr/split_stream

	test -f venv/bin/activate || virtualenv -p $(shell which python) venv

	number=1 ; while [ $$number -le 6 ] ; do \
		venv/bin/python atlas_splitter.py \
			-d ../../../data/atlasv2/data/attack/h1/cbc-edr \
			-i edr-h1-m$$number \
			-b split_base/atlas-base-h1-attack-m$$number \
			-s split_stream/atlas-stream-h1-attack-m$$number ; \
		number=`expr $$number + 1` ; \
	done 

	number=1 ; while [ $$number -le 6 ] ; do \
		venv/bin/python atlas_splitter.py \
			-d ../../../data/atlasv2/data/attack/h2/cbc-edr \
			-i edr-h2-m$$number \
			-b split_base/atlas-base-h2-attack-m$$number \
			-s split_stream/atlas-stream-h2-attack-m$$number ; \
		number=`expr $$number + 1` ; \
	done

	number=1 ; while [ $$number -le 4 ] ; do \
		venv/bin/python atlas_splitter.py \
			-d ../../../data/atlasv2/data/attack/h1/cbc-edr \
			-i edr-h1-s$$number \
			-b split_base/atlas-base-h1-attack-s$$number \
			-s split_stream/atlas-stream-h1-attack-s$$number ; \
		number=`expr $$number + 1` ; \
	done 

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

clean_base_and_stream:
	rm -f ../../../data/atlasv2/data/benign/h1/cbc-edr/base ../../../data/atlasv2/data/benign/h1/cbc-edr/stream
	rm -rf venv
