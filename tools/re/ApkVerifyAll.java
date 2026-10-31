// Usage: javac -cp ~/Android/Sdk/build-tools/37.0.0/lib/apksigner.jar ApkVerifyAll.java; java -cp .:apksigner.jar ApkVerifyAll <file with one APK path per line>. Result lines: status, schemes, signer id, path, first error.
import com.android.apksig.ApkVerifier;
import java.io.File;
import java.nio.file.*;
import java.security.MessageDigest;
import java.security.cert.X509Certificate;
import java.util.*;

/** Verify every APK listed in a file with the real apksig library: ApkVerifyAll <list> -> lines "status<TAB>schemes<TAB>signerSha256<TAB>path<TAB>first error" */
public class ApkVerifyAll {
    public static void main(String[] a) throws Exception {
        for (String p : Files.readAllLines(Paths.get(a[0]))) {
            if (p.isBlank()) continue;
            String status, schemes = "", sha = "", err = "";
            try {
                ApkVerifier.Result r = new ApkVerifier.Builder(new File(p)).setMinCheckedPlatformVersion(31).build().verify();
                status = r.isVerified() ? "OK" : "FAIL";
                schemes = (r.isVerifiedUsingV1Scheme() ? "v1 " : "") + (r.isVerifiedUsingV2Scheme() ? "v2 " : "") + (r.isVerifiedUsingV3Scheme() ? "v3 " : "");
                List<X509Certificate> cs = r.getSignerCertificates();
                if (cs != null && !cs.isEmpty()) {
                    StringBuilder sb = new StringBuilder();
                    for (X509Certificate c : cs) {   // every signer certificate, full SHA-256, comma separated
                        byte[] d = MessageDigest.getInstance("SHA-256").digest(c.getEncoded());
                        if (sb.length() > 0) sb.append(',');
                        for (byte x : d) sb.append(String.format("%02x", x));
                    }
                    sha = sb.toString();
                }
                for (ApkVerifier.IssueWithParams e : r.getErrors()) { err = e.toString(); break; }
                if (err.isEmpty()) for (ApkVerifier.Result.V2SchemeSignerInfo s : r.getV2SchemeSigners()) for (ApkVerifier.IssueWithParams e : s.getErrors()) { err = e.toString(); break; }
            } catch (Throwable t) { status = "EXC"; err = t.toString(); }
            System.out.println(status + "\t" + schemes.trim() + "\t" + sha + "\t" + p + "\t" + err.replace('\t',' '));
        }
    }
}
