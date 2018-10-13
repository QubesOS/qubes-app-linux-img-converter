ifeq ($(PACKAGE_SET),dom0)
RPM_SPEC_FILES := rpm_spec/qimg-converter-dom0.spec
else ifeq ($(PACKAGE_SET),vm)
  ifneq ($(filter $(DISTRIBUTION), debian qubuntu),)
    DEBIAN_BUILD_DIRS := debian
  endif

  RPM_SPEC_FILES := rpm_spec/qimg-converter.spec
endif

# vim: filetype=make
#
