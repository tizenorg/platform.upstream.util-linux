#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <getopt.h>

#ifdef HAVE_SYS_SWAP_H
# include <sys/swap.h>
#endif

#include "nls.h"
#include "loop.h"
#include "c.h"
#include "closestream.h"

#include "swapon-common.h"

#ifndef SWAPON_HAS_TWO_ARGS
/* libc is insane, let's call the kernel */
# include <sys/syscall.h>
# define swapoff(path) syscall(SYS_swapoff, path)
#endif

static int verbose;
static int all;

#define QUIET	1
#define CANONIC	1

static int do_swapoff(const char *orig_special, int quiet, int canonic)
{
        const char *special = orig_special;

	if (verbose)
		printf(_("swapoff %s\n"), orig_special);

	if (!canonic) {
		special = mnt_resolve_spec(orig_special, mntcache);
		if (!special)
			return cannot_find(orig_special);
	}

	if (swapoff(special) == 0)
		return 0;	/* success */

	if (errno == EPERM)
		errx(EXIT_FAILURE, _("Not superuser."));

	if (!quiet || errno == ENOMEM)
		warn(_("%s: swapoff failed"), orig_special);

	return -1;
}

static int swapoff_by_label(const char *label, int quiet)
{
	const char *special = mnt_resolve_tag("LABEL", label, mntcache);
	return special ? do_swapoff(special, quiet, CANONIC) : cannot_find(label);
}

static int swapoff_by_uuid(const char *uuid, int quiet)
{
	const char *special = mnt_resolve_tag("UUID", uuid, mntcache);
	return special ? do_swapoff(special, quiet, CANONIC) : cannot_find(uuid);
}

static void __attribute__ ((__noreturn__)) usage(FILE * out)
{
	fputs(USAGE_HEADER, out);

	fprintf(out, _(" %s [options] [<spec>]\n"), program_invocation_short_name);

	fputs(USAGE_OPTIONS, out);
	fputs(_(" -a, --all              disable all swaps from /proc/swaps\n"
		" -v, --verbose          verbose mode\n"), out);

	fputs(USAGE_SEPARATOR, out);
	fputs(USAGE_HELP, out);
	fputs(USAGE_VERSION, out);

	fputs(_("\nThe <spec> parameter:\n" \
		" -L <label>             LABEL of device to be used\n" \
		" -U <uuid>              UUID of device to be used\n" \
		" LABEL=<label>          LABEL of device to be used\n" \
		" UUID=<uuid>            UUID of device to be used\n" \
		" <device>               name of device to be used\n" \
		" <file>                 name of file to be used\n"), out);

	fprintf(out, USAGE_MAN_TAIL("swapoff(8)"));
	exit(out == stderr ? EXIT_FAILURE : EXIT_SUCCESS);
}

static void
shutdown_encrypted_swap(char *loop)
{
	int fd;
	struct stat statbuf;
	struct loop_info64 loopinfo;
	unsigned char b[32];
	FILE *f;
	size_t ignoreThis = 0;

	if(stat(loop, &statbuf) == 0 && S_ISBLK(statbuf.st_mode)) {
		if((fd = open(loop, O_RDWR)) >= 0) {
			if(!loop_get_status64_ioctl(fd, &loopinfo)) {
				/*
				 * Read 32 bytes of random data from kernel's random
				 * number generator and write that to loop device.
				 * This preserves some of kernel's random entropy
				 * to next activation of encrypted swap on this
				 * partition.
				 */
				if((f = fopen("/dev/urandom", "r")) != NULL) {
					ignoreThis += fread(&b[0], 32, 1, f);
					fclose(f);
					ignoreThis += write(fd, &b[0], 32);
					fsync(fd);
				}
			}
			close(fd);
		}
		sync();
		if((fd = open(loop, O_RDONLY)) >= 0) {
			if(!loop_get_status64_ioctl(fd, &loopinfo)) {
				ioctl(fd, LOOP_CLR_FD, 0);
			}
			close(fd);
		}
	}
}

static int swapoff_all(void)
{
	int status = 0;
	struct libmnt_table *tb;
	struct libmnt_fs *fs;
	struct libmnt_iter *itr = mnt_new_iter(MNT_ITER_BACKWARD);

	if (!itr)
		err(EXIT_FAILURE, _("failed to initialize libmount iterator"));

	/*
	 * In case /proc/swaps exists, unswap stuff listed there.  We are quiet
	 * but report errors in status.  Errors might mean that /proc/swaps
	 * exists as ordinary file, not in procfs.  do_swapoff() exits
	 * immediately on EPERM.
	 */
	tb = get_swaps();

	while (tb && mnt_table_find_next_fs(tb, itr, match_swap, NULL, &fs) == 0)
		status |= do_swapoff(mnt_fs_get_source(fs), QUIET, CANONIC);

	/*
	 * Unswap stuff mentioned in /etc/fstab.  Probably it was unmounted
	 * already, so errors are not bad.  Doing swapoff -a twice should not
	 * give error messages.
	 */
	tb = get_fstab();
	mnt_reset_iter(itr, MNT_ITER_FORWARD);

	while (tb && mnt_table_find_next_fs(tb, itr, match_swap, NULL, &fs) == 0) {
		char *special;
		char *loop = NULL, *encryption = NULL;
		char *val = NULL;
		size_t len = 0;

		special = (char *) mnt_fs_get_source(fs);
		if(!special) continue;
		if(mnt_fs_get_option(fs, "loop", &val, &len) == 0 && val && len)
			loop = strndup(val, len);
		if(mnt_fs_get_option(fs, "encryption", &val, &len) == 0 && val && len)
			encryption = strndup(val, len);
		if (loop && encryption) {
			if (!is_active_swap(loop)) {	/* do this only if it was not in /proc/swaps */
				do_swapoff(loop, QUIET, !CANONIC);
			}
			shutdown_encrypted_swap(loop);
			goto do_free;
		}
		if (!is_active_swap(special)) {		/* do this only if it was not in /proc/swaps */
			do_swapoff(special, QUIET, !CANONIC);
		}
		do_free:
		if(loop) free(loop);
		if(encryption) free(encryption);
	}

	mnt_free_iter(itr);
	return status;
}

int main(int argc, char *argv[])
{
	int status = 0, c;
	size_t i;

	static const struct option long_opts[] = {
		{ "all", 0, 0, 'a' },
		{ "help", 0, 0, 'h' },
		{ "verbose", 0, 0, 'v' },
		{ "version", 0, 0, 'V' },
		{ NULL, 0, 0, 0 }
	};

	setlocale(LC_ALL, "");
	bindtextdomain(PACKAGE, LOCALEDIR);
	textdomain(PACKAGE);
	atexit(close_stdout);

	while ((c = getopt_long(argc, argv, "ahvVL:U:",
				 long_opts, NULL)) != -1) {
		switch (c) {
		case 'a':		/* all */
			++all;
			break;
		case 'h':		/* help */
			usage(stdout);
			break;
		case 'v':		/* be chatty */
			++verbose;
			break;
		case 'V':		/* version */
			printf(UTIL_LINUX_VERSION);
			return EXIT_SUCCESS;
		case 'L':
			add_label(optarg);
			break;
		case 'U':
			add_uuid(optarg);
			break;
		case '?':
		default:
			usage(stderr);
		}
	}
	argv += optind;

	if (!all && !numof_labels() && !numof_uuids() && *argv == NULL)
		usage(stderr);

	mnt_init_debug(0);
	mntcache = mnt_new_cache();

	for (i = 0; i < numof_labels(); i++)
		status |= swapoff_by_label(get_label(i), !QUIET);

	for (i = 0; i < numof_uuids(); i++)
		status |= swapoff_by_uuid(get_uuid(i), !QUIET);

	while (*argv != NULL)
		status |= do_swapoff(*argv++, !QUIET, !CANONIC);

	if (all)
		status |= swapoff_all();

	free_tables();
	mnt_unref_cache(mntcache);

	return status;
}
