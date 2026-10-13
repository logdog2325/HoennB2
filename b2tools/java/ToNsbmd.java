import ctrmap.formats.generic.collada.DAE;
import ctrmap.formats.generic.xobj.OBJFile;
import ctrmap.formats.ntr.nitrowriter.common.NNSWriterLogger;
import ctrmap.formats.ntr.nitrowriter.nsbmd.NSBMDExportSettings;
import ctrmap.formats.ntr.nitrowriter.nsbmd.NSBMDWriter;
import ctrmap.formats.ntr.nitrowriter.nsbtx.NSBTXWriter;
import ctrmap.renderer.scene.texturing.Texture;
import ctrmap.renderer.scenegraph.G3DResource;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Convert a DAE/OBJ model to a Nitro NSBMD using CTRMapV's own writer (no Nintendo SDK tools).
 *
 *   java -cp work/java:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar ToNsbmd IN.dae OUT.nsbmd PALETTES.txt [OUT.nsbtx]
 *
 * PALETTES.txt has one "texture palette" pair per line. Every texture the model uses must be listed, so each
 * material binds to the palette the game's texture file actually holds (usually texture_pl, not always).
 * Without OUT.nsbtx the model is written without textures, as the game's map chunks and buildings are.
 *
 *   java ... ToNsbmd --batch LIST.txt PALETTES.txt      (LIST: one "IN.dae OUT.nsbmd" pair per line; one JVM start)
 *
 * A leading --vcol writes the DAE's vertex colours instead of its normals (unlit, like Black 2's own interior rooms,
 * whose shading is baked into vertex colours; b2tools/models_interior.py). Without it: normals, as before.
 * A leading --tex also puts the model's textures (its PNGs, converted by CTRMapV's texture writer) inside the NSBMD,
 * as Black 2's stand-alone models carry theirs (the trainer card's 3D badges: b2tools/trainer_card_models.py).
 */
public class ToNsbmd {
    static boolean vcol = false;
    static boolean tex = false;

    public static void main(String[] a) throws Exception {
        while (a.length > 0 && (a[0].equals("--vcol") || a[0].equals("--tex"))) {
            if (a[0].equals("--vcol")) vcol = true; else tex = true;
            a = java.util.Arrays.copyOfRange(a, 1, a.length);
        }
        if (a[0].equals("--batch")) {
            for (String line : Files.readAllLines(Paths.get(a[1]))) {
                String[] p = line.trim().split("\\s+");
                if (p.length == 2) convert(new String[] {p[0], p[1], a[2]});
            }
            return;
        }
        convert(a);
    }

    static void convert(String[] a) throws Exception {
        File in = new File(a[0]);
        G3DResource res = in.getName().toLowerCase().endsWith(".dae") ? new DAE(in).toGeneric() : new OBJFile(in).toGeneric();
        Map<String, String> pal = new HashMap<>();
        for (String line : Files.readAllLines(Paths.get(a[2]))) {
            String[] p = line.trim().split("\\s+");
            if (p.length == 2 && !p[0].startsWith("#")) pal.put(p[0], p[1]);
        }
        List<Texture> texs = res.textures;
        StringBuilder missing = new StringBuilder();
        for (Texture t : texs) {
            String p = pal.get(t.name);
            if (p == null) { missing.append(' ').append(t.name); continue; }
            t.metaData.putValue("IdxFormatPaletteName", p);
        }
        if (missing.length() > 0) {
            System.err.println(a[0] + ": no palette listed for:" + missing);
            System.exit(2);
        }
        boolean withTex = a.length > 3;
        // (includeModels, includeTextures, preferVColOverNormal, makePolystrips, minPolystripPrims, jointsAsVisGroups, omitUnusedTextures)
        NSBMDExportSettings s = new NSBMDExportSettings(true, tex, vcol, true, -1, true, true);
        byte[] mdl = new NSBMDWriter(res, s, new NNSWriterLogger.DummyLogger()).writeToMemory();
        Files.write(Paths.get(a[1]), mdl);
        System.out.println(a[1] + ": " + mdl.length + " bytes, " + res.models.size() + " model(s), " + texs.size() + " textures bound by name");
        if (withTex) {
            byte[] tex = new NSBTXWriter(texs, new NNSWriterLogger.DummyLogger()).writeToMemory();
            Files.write(Paths.get(a[3]), tex);
            System.out.println(a[3] + ": " + tex.length + " bytes");
        }
    }
}
