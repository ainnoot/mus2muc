clean:
	make -C wasp clean
	rm -rf wasp/build/release
	make -C aaltaf clean
	rm -f bin/*

create_bin_folder:
	mkdir -p bin

patch_wasp:
	patch -N -r - --silent -p0 -i Mus.cpp_patch || true
	patch -N -r - --silent -p0 -i Mus.h_patch || true

compile_aaltaf:
	make -j clean -C aaltaf
	make -C aaltaf -j
	cp aaltaf/aaltaf bin/aaltaf

compile_wasp: patch_wasp
	make -j -C wasp BUILD=release
	cp wasp/build/release/wasp bin/

install: create_bin_folder compile_wasp compile_aaltaf
