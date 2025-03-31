import sys
import random
import struct
from enum import IntEnum

class FakeJPEG:
    # Given a bunch of JPEG files, this class builds a set of
    # templates which can later be used to generate fake jpeg
    # files containing random pixel data.
    #
    # The general idea is that if you want to generate a large
    # number of things that look like JPEGs quickly, this lets
    # you do it. Feed the class a collection of real files, save
    # the resulting object using e.g. pickle. Later, you can
    # load the pickle and call the object's "generate" method
    # to get a sorta-kinda-JPEG file.
    #
    # N.B. The result is *not* a fully valid JPEG. The random
    # data that gets filled out doesn't necessarily comprise
    # of valid Huffman codes. But I've not yet found a decoder
    # which doesn't emit pixel data when handed one of the
    # generated files.

    # Enum type for the various JPEG chunk markers.
    class markers(IntEnum):
        SOI   = 0xFFD8
        EOI   = 0xFFD9
        SOS   = 0xFFDA
        APP0  = 0xFFE0
        APP1  = 0xFFE1
        APP2  = 0xFFE2
        APP3  = 0xFFE3
        APP4  = 0xFFE4
        APP5  = 0xFFE5
        APP6  = 0xFFE6
        APP7  = 0xFFE7
        APP8  = 0xFFE8
        APP9  = 0xFFE9
        APP10 = 0xFFEA
        APP11 = 0xFFEB
        APP12 = 0xFFEC
        APP13 = 0xFFED
        APP14 = 0xFFEE
        APP15 = 0xFFEF
        COM   = 0xFFFE

    # Hand it a list of jpegs and it'll build a set of templates.
    # You'd probably do this as a one-off and store the resulting
    # object using e.g. pickle.
    #
    # If you pass in a "logging" object, exceptions reading files
    # will be reported via logger.warning().
    def __init__(self, jpegs, logger=None):
        self.templates = []
        for jpg in jpegs:
            if logger is not None:
                logger.debug(f"Loading {jpg}")
            try:
                # Read the JPEG.
                with open(jpg, 'rb') as f:
                    data = f.read()

                chunks = []
                # Step through the JPEG, one chunk at a time,
                # until the data is exhausted.
                while True:
                    # Get the marker ID.
                    marker, = struct.unpack(">H", data[0:2])

                    # Check it's valid. If not, we'll skip this jpeg.
                    if (marker & 0xFF00) != 0xFF00:
                        raise Exception("Bad marker {marker:04x} encountered")

                    if marker == FakeJPEG.markers.SOI:
                        # Start of image - no "length" field.
                        chunks.append([marker, data[0:2]])
                        data = data[2:]
                    elif marker == FakeJPEG.markers.EOI:
                        # End of image - no "length" field.
                        chunks.append([marker, data[0:2]])
                        break
                    elif marker == FakeJPEG.markers.SOS:
                        # Start of scan. There's a "length"
                        # field which identifies a preamble that
                        # we need to keep. Then there's pixel
                        # data which we need to scan up to
                        # the next chunk marker. We throw that
                        # data away and just remember its length.
                        lenhdr, = struct.unpack(">H", data[2:4])
                        pos = 2 + lenhdr

                        # Step through the scan data, looking for the
                        # end marker.
                        while pos < len(data)-1:
                            # 0xFF in the stream is escaped with a following
                            # 0x00 if it's not an actual chunk marker.
                            if data[pos] == 0xFF and data[pos+1] != 0x00:
                                break
                            pos += 1
                        # Store the preamble and the scan data length.
                        chunks.append([marker, [ data[0:lenhdr+2], pos-lenhdr-2 ]])
                        data = data[pos:]
                    elif marker == FakeJPEG.markers.APP0:
                        # The "JFIF" chunk - this could have thumbnail
                        # data, so we want to remove that, if present.
                        lenchunk, = struct.unpack(">H", data[2:4])
                        jfif = data[0:2+lenchunk]
                        data = data[2+lenchunk:]

                        # Thumbnail?
                        if len(jfif)  > 18:
                            jbytes = list(jfif[0:18])
                            jbytes[2] = 0
                            jbytes[3] = 16
                            jbytes[16] = 0
                            jbytes[17] = 0
                            jfif = bytes(jbytes)
                            print(jfif)
                        chunks.append([marker, jfif])
                    else:
                        # Other markers all have a length field, I think.
                        lenchunk, = struct.unpack(">H", data[2:4])

                        # Drop APP* markers - these will contain e.g. exif
                        # data, which we won't want to put into generated
                        # fake JPEGs.
                        if marker not in (
                            FakeJPEG.markers.APP1,
                            FakeJPEG.markers.APP2, FakeJPEG.markers.APP3,
                            FakeJPEG.markers.APP4, FakeJPEG.markers.APP5,
                            FakeJPEG.markers.APP6, FakeJPEG.markers.APP7,
                            FakeJPEG.markers.APP8, FakeJPEG.markers.APP9,
                            FakeJPEG.markers.APP10, FakeJPEG.markers.APP11,
                            FakeJPEG.markers.APP12, FakeJPEG.markers.APP13,
                            FakeJPEG.markers.APP14, FakeJPEG.markers.APP15,
                            FakeJPEG.markers.COM
                        ):
                            # Yes, we want this chunk. Add it to the list.
                            chunks.append([marker, data[0:2+lenchunk]])
                        data = data[2+lenchunk:]
                    if len(data)==0:
                        raise Exception("End of file reached without finding an end tag")

                # OK, we successfully parsed this JPEG. Add it to our
                # list of templates.
                self.templates.append(chunks)
            except Exception as e:
                # If handed a logger, use it to report the issue. Otherwise
                # silently skip the JPEG.
                if logger is not None:
                    logger.warning(f"Failed to decode {jpg}: {e}")

    # Generate a fake jpeg using our template data and
    # return it as bytes. If handed a random number generator
    # object, use that for generating the required random data.
    def generate(self, comment=None, rng=random):
        # Choose a random template from our set.
        # This could raise an exception if we've not got
        # any templates. Allow that exception to propagate.
        template = rng.choice(self.templates)

        # Where we'll accumulate the chunks of our fake JPEG.
        chunks = []

        # For each chunk in the template...
        for marker, data in template:
            if marker != FakeJPEG.markers.SOS:
                # Everything other than an SOS scan just gets added
                # as-is.
                chunks.append(data)
            else:
                preamble, length = data

                # This chunk is scan data. The first part is the header
                # of the scan data, and the second is the compressed
                # data.
                chunks.append(preamble)

                # Generate a bunch of random bytes, roughly as long as
                # the length that the template JPEG contained in this chunk.
                scandata = rng.randbytes(rng.randint(int(length), int(1.1*length)))

                # Totally random data gives rise to frequent bad Huffman
                # codes. While we *could* generate perfect data by examining
                # the DHT data (or constructing it really carefully), we're
                # more interested in speed than correctness. Long runs of
                # 1's in the random bit stream increase the likelihood of
                # generating invalid Huffman data. So we mask out a few bits
                # from each byte. A mask of 0x6d seems to work fairly well.
                #
                # The trick below masks bits from scandata fairly quickly -
                # much more quickly than the naiive list comprehension would.
                # Idea from # https://stackoverflow.com/questions/46540337/
                scandata = (int.from_bytes(scandata, byteorder="little", signed=False) & int("0x" + ("6d" * len(scandata)), 16)).to_bytes(len(scandata), "little")

                # With the masking above, we don't have to do the following,
                # since 0xFF can't exist within the data.
                # Any cases of 0xFF in the scan data need to be escaped by
                # adding an 0x00 after them.
                # scandata = scandata.replace(b"\xff", b"\xff\x00")

                # Add this chunk to our collection.
                chunks.append(scandata)

        # If a comment was specified, shove it into the chunk array
        # after the first two chunks.
        if comment is not None:
            comment = comment.encode("utf-8")
            chunk = struct.pack(f">HH{len(comment)}s", 0xFFFE, len(comment)+2, comment)
            chunks = chunks[0:2] + [chunk] + chunks[2:]

        # Finally, join all the genrated chunks and return the result.
        return b"".join(chunks)
