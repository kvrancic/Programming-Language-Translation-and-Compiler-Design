import java.util.Arrays;
import java.util.LinkedList;
import java.util.Scanner;

public class SemantickiAnalizator {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        LinkedList<Integer> retciDefinicije = new LinkedList<>();
        LinkedList<String> leksJedinke = new LinkedList<>();
        LinkedList<Integer> dubinaBlokaJedinki = new LinkedList<>();

        int trenutnaDubinaBloka = 0;

        String input;
        String prevLine = "";

        while (sc.hasNextLine()) {
            input = sc.nextLine().trim();

            if (input == "") {
                break;
            }

            if (input.split(" ")[0].equals("KR_ZA")) {
                trenutnaDubinaBloka++;
            } else if (input.split(" ")[0].equals("KR_AZ")) {
                for (int i = 0; i < leksJedinke.size(); i++) {
                    if (trenutnaDubinaBloka == dubinaBlokaJedinki.get(i)) {
                        retciDefinicije.remove(i);
                        leksJedinke.remove(i);
                        dubinaBlokaJedinki.remove(i);
                        i--;
                    }
                }

                trenutnaDubinaBloka--;
            }


            if (input.split(" ")[0].equals("IDN")) {
                boolean jedinkaDefinirana = false;
                for (String jedinka : leksJedinke) {
                    if (input.split(" ")[2].equals(jedinka)) {
                        jedinkaDefinirana = true;
                    }
                }

                if (!prevLine.equals("<P>") && (jedinkaDefinirana == false
                        || prevLine.split(" ")[0].equals("KR_ZA"))) {

                    retciDefinicije.add(Integer.parseInt(input.split(" ")[1]));
                    leksJedinke.add(input.split(" ")[2]);
                    dubinaBlokaJedinki.add(trenutnaDubinaBloka);
                } else if (!prevLine.equals("<naredba_pridruzivanja>") && !(!prevLine.equals("<P>") && (jedinkaDefinirana == false
                        || prevLine.split(" ")[0].equals("KR_ZA")))) {

                    String leksJedinka = null;
                    Integer redakDefinicije = null;


//                    System.out.println(leksJedinke + retciDefinicije.toString());
                    if (!(leksJedinke.getLast().equals(input.split(" ")[2])
                            && retciDefinicije.getLast() == Integer.parseInt(input.split(" ")[1]))) {

                        for (int i = 0; i < leksJedinke.size(); i++) {
                            if (input.split(" ")[2].equals(leksJedinke.get(i))) {
                                leksJedinka = leksJedinke.get(i);
                                redakDefinicije = retciDefinicije.get(i);
                            }
                        }
                    }

                    if (leksJedinka != null) {
                        System.out.println(input.split(" ")[1] + " "
                                + redakDefinicije + " "
                                + leksJedinka);
                    } else {
                        System.out.println("err "
                                + input.split(" ")[1] + " "
                                + input.split(" ")[2]);
                        break;
                    }
                }
            }

            prevLine = input;
        }
    }
}