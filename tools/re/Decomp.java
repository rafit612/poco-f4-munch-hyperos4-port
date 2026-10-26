import jadx.api.*;
import java.io.File;

/** Decompile selected classes of an APK/DEX with the JADX library: Decomp <apk> <regex on class name>... */
public class Decomp {
    public static void main(String[] a) throws Exception {
        JadxArgs args = new JadxArgs();
        args.setInputFile(new File(a[0]));
        args.setOutDir(new File("/tmp/jdx_unused"));
        args.setSkipResources(true);
        args.setShowInconsistentCode(true);
        try (JadxDecompiler d = new JadxDecompiler(args)) {
            d.load();
            for (JavaClass c : d.getClasses())
                for (int i = 1; i < a.length; i++)
                    if (c.getFullName().matches(a[i]) || c.getRawName().matches(a[i])) {
                        System.out.println("// ===== " + c.getRawName() + " (" + c.getFullName() + ")");
                        System.out.println(c.getCode());
                    }
        }
    }
}
