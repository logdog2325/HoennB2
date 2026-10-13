import ctrmap.formats.ntr.nitroreader.nsbtx.NSBTX;
import ctrmap.formats.ntr.nitroreader.nsbtx.NSBTXPalette;
import ctrmap.formats.ntr.nitroreader.nsbtx.NSBTXTexture;
import ctrmap.formats.ntr.nitrowriter.common.NNSWriterLogger;
import ctrmap.formats.ntr.nitrowriter.nsbtx.NSBTXWriter;
import ctrmap.renderer.scene.texturing.Texture;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Rebuild a Nitro texture file, optionally adding textures copied from other texture files.
 *
 *   java ... MergeNsbtx BASE.nsbtx OUT.nsbtx [PAIRS.txt] [SRC.nsbtx:texture[:palette] ...]
 *
 * Every texture keeps its name and its palette name. PAIRS.txt ("texture palette" per line, taken from the game's
 * own models) says which palette goes with which texture; otherwise "texture_pl", or none for direct colour.
 */
public class MergeNsbtx {
    static final Map<String, String> PAIRS = new java.util.HashMap<>();

    static String paletteFor(NSBTX f, String tex, String explicit) {
        if (explicit != null) return explicit;
        if (PAIRS.containsKey(tex)) return PAIRS.get(tex);
        if (f.TEX0.getPalette(tex + "_pl") != null) return tex + "_pl";
        String cut = (tex + "_pl").length() > 16 ? (tex + "_pl").substring(0, 16) : null;
        if (cut != null && f.TEX0.getPalette(cut) != null) return cut;
        return null;  // direct-colour textures have no palette
    }

    static Texture convert(NSBTX f, String tex, String pal) {
        Texture t = f.TEX0.getConvTexture(tex, pal);
        if (t == null) throw new IllegalArgumentException("texture not found: " + tex);
        if (pal != null) t.metaData.putValue("IdxFormatPaletteName", pal);
        return t;
    }

    public static void main(String[] a) throws Exception {
        int first = 2;
        if (a.length > 2 && a[2].endsWith(".txt")) {
            for (String line : Files.readAllLines(Paths.get(a[2]))) {
                String[] p = line.replace("\"", "").trim().split("\\s+");
                if (p.length == 2) PAIRS.put(p[0], p[1]);
            }
            first = 3;
        }
        NSBTX base = new NSBTX(Files.readAllBytes(Paths.get(a[0])));
        Map<String, Texture> out = new LinkedHashMap<>();
        for (NSBTXTexture t : base.TEX0.textures) out.put(t.name, convert(base, t.name, paletteFor(base, t.name, null)));
        Map<String, NSBTX> cache = new LinkedHashMap<>();
        for (int i = first; i < a.length; i++) {
            String[] p = a[i].split(":");
            NSBTX src = cache.computeIfAbsent(p[0], k -> { try { return new NSBTX(Files.readAllBytes(Paths.get(k))); } catch (Exception e) { throw new RuntimeException(e); } });
            if (out.containsKey(p[1])) { System.err.println("already present, skipped: " + p[1]); continue; }
            out.put(p[1], convert(src, p[1], paletteFor(src, p[1], p.length > 2 ? p[2] : null)));
        }
        List<Texture> list = new ArrayList<>(out.values());
        byte[] data = new NSBTXWriter(list, new NNSWriterLogger.DummyLogger()).writeToMemory();
        Files.write(Paths.get(a[1]), data);
        System.out.println(a[1] + ": " + list.size() + " textures, " + data.length + " bytes (base " + Files.size(Paths.get(a[0])) + ")");
    }
}
