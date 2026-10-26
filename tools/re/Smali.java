import com.android.tools.smali.baksmali.Baksmali;
import com.android.tools.smali.baksmali.BaksmaliOptions;
import com.android.tools.smali.dexlib2.DexFileFactory;
import com.android.tools.smali.dexlib2.Opcodes;
import com.android.tools.smali.dexlib2.iface.DexFile;
import com.android.tools.smali.smali.SmaliOptions;
import java.io.File;
import java.util.Collections;

/** Smali d <in.dex> <outdir>  — disassemble;  Smali a <smalidir> <out.dex> <api> — assemble. */
public class Smali {
    public static void main(String[] a) throws Exception {
        if (a[0].equals("d")) {
            DexFile dex = DexFileFactory.loadDexFile(new File(a[1]), Opcodes.getDefault());
            BaksmaliOptions o = new BaksmaliOptions();
            if (!Baksmali.disassembleDexFile(dex, new File(a[2]), 8, o)) System.exit(1);
        } else {
            SmaliOptions o = new SmaliOptions();
            o.outputDexFile = a[2];
            o.apiLevel = Integer.parseInt(a[3]);
            o.jobs = 8;
            if (!com.android.tools.smali.smali.Smali.assemble(o, Collections.singletonList(a[1]))) System.exit(1);
        }
    }
}
