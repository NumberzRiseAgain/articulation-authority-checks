# Numberz.ai Inc.  Raghu Venkat (PI), Dr. Tricha Anjali.  Company-funded, September 2026.
# Feasibility study for DON26BZ05-NV071 (Navy / NAVAIR, SBIR Phase I). No Government funding.
# Released under the MIT License; see LICENSE at the repository root.
"""
SPOKELINE — surrogate S1000D corpus generator.

SURROGATE DATA. Every document written by this script was authored by Numberz.ai for
demonstration. Nothing here is Navy technical data, and the equipment is a bicycle.
The Model Ident Code SPOKE1 is fictional.

The real substrate for Phase I is the public S1000D Bike Data Set (Mountain Storm Mk1,
Issue 4.2). This generator produces the same shapes so the extractor can be pointed at
the real set without change.
"""
import os, textwrap

DM = {}

DM["DMC-SPOKE1-A-24-10-01-00A-941A-D"] = """<?xml version="1.0" encoding="UTF-8"?>
<!-- SURROGATE. Authored by Numberz.ai. Not Navy technical data. -->
<dmodule>
  <identAndStatusSection>
    <dmAddress>
      <dmIdent><dmCode modelIdentCode="SPOKE1" systemCode="24" subSystemCode="1"
        subSubSystemCode="0" assyCode="01" disassyCode="00" infoCode="941"/></dmIdent>
      <dmAddressItems><dmTitle><techName>Front wheel and brake assembly</techName>
        <infoName>Illustrated parts data</infoName></dmTitle></dmAddressItems>
    </dmAddress>
    <dmStatus><security securityClassification="01"/>
      <dataRestrictions>Distribution Statement A. Approved for public release.</dataRestrictions>
    </dmStatus>
  </identAndStatusSection>
  <content><illustratedPartsCatalog>
    <catalogSeqNumber item="001" partNumber="SPK-1000" parent=""><partName>frame</partName></catalogSeqNumber>
    <catalogSeqNumber item="002" partNumber="SPK-1100" parent="SPK-1000"><partName>fork</partName></catalogSeqNumber>
    <catalogSeqNumber item="003" partNumber="SPK-1110" parent="SPK-1100"><partName>handlebar</partName></catalogSeqNumber>
    <catalogSeqNumber item="004" partNumber="SPK-1200" parent="SPK-1100"><partName>front wheel</partName></catalogSeqNumber>
    <catalogSeqNumber item="005" partNumber="SPK-1210" parent="SPK-1200"><partName>axle skewer</partName></catalogSeqNumber>
    <catalogSeqNumber item="006" partNumber="SPK-1211" parent="SPK-1210"><partName>skewer lever</partName></catalogSeqNumber>
    <catalogSeqNumber item="007" partNumber="SPK-1212" parent="SPK-1210"><partName>quick release nut</partName></catalogSeqNumber>
    <catalogSeqNumber item="008" partNumber="SPK-1300" parent="SPK-1100"><partName>brake caliper arm left</partName></catalogSeqNumber>
    <catalogSeqNumber item="009" partNumber="SPK-1301" parent="SPK-1100"><partName>brake caliper arm right</partName></catalogSeqNumber>
    <catalogSeqNumber item="010" partNumber="SPK-1310" parent="SPK-1300"><partName>brake pad left</partName></catalogSeqNumber>
    <catalogSeqNumber item="011" partNumber="SPK-1311" parent="SPK-1301"><partName>brake pad right</partName></catalogSeqNumber>
    <catalogSeqNumber item="012" partNumber="SPK-1400" parent="SPK-1110"><partName>brake lever</partName></catalogSeqNumber>
    <catalogSeqNumber item="013" partNumber="SPK-1500" parent="SPK-1100"><partName>fender bolt</partName></catalogSeqNumber>
  </illustratedPartsCatalog></content>
</dmodule>
"""

DM["DMC-SPOKE1-A-24-10-01-00A-520A-D"] = """<?xml version="1.0" encoding="UTF-8"?>
<!-- SURROGATE. Authored by Numberz.ai. Not Navy technical data. -->
<dmodule>
  <identAndStatusSection>
    <dmAddress>
      <dmIdent><dmCode modelIdentCode="SPOKE1" systemCode="24" subSystemCode="1"
        subSubSystemCode="0" assyCode="01" disassyCode="00" infoCode="520"/></dmIdent>
      <dmAddressItems><dmTitle><techName>Front wheel</techName>
        <infoName>Remove procedure</infoName></dmTitle></dmAddressItems>
    </dmAddress>
    <dmStatus><security securityClassification="01"/>
      <dataRestrictions>Distribution Statement A. Approved for public release.</dataRestrictions>
    </dmStatus>
  </identAndStatusSection>
  <content><procedure>
    <preliminaryRqmts>
      <reqCondGroup><reqCondNoRef><reqCond>Bicycle supported in a maintenance stand.</reqCond></reqCondNoRef></reqCondGroup>
      <reqSupportEquipDescrGroup>
        <supportEquipDescr id="tool-5mm"><name>5 mm hex key</name></supportEquipDescr>
      </reqSupportEquipDescrGroup>
    </preliminaryRqmts>
    <mainProcedure>
      <proceduralStep id="stp-010" partRef="SPK-1400" motion="revolute" axis="X" sense="positive"
                      travelStart="0" travelEnd="42" travelUnit="deg">
        <warning id="wrn-010">Do not remove the wheel with the bicycle unsupported. The machine will fall.</warning>
        <para>Squeeze the brake lever and release the caliper quick release.</para>
      </proceduralStep>
      <proceduralStep id="stp-020" partRef="SPK-1211" motion="revolute" axis="Z" sense="positive"
                      travelStart="0" travelEnd="180" travelUnit="deg">
        <para>Open the skewer lever fully.</para>
      </proceduralStep>
      <proceduralStep id="stp-030" partRef="SPK-1212" motion="revolute" axis="X" sense="negative"
                      travelStart="0" travelEnd="1800" travelUnit="deg" toolRef="tool-5mm">
        <caution id="cau-030">Do not remove the quick release nut completely. It will be lost.</caution>
        <para>Turn the quick release nut counter-clockwise five turns to loosen.</para>
      </proceduralStep>
      <proceduralStep id="stp-040" partRef="SPK-1210" motion="prismatic" axis="X" sense="positive"
                      travelStart="0" travelEnd="150" travelUnit="mm">
        <para>Withdraw the axle skewer from the hub.</para>
      </proceduralStep>
      <proceduralStep id="stp-050" partRef="SPK-1200" motion="prismatic" axis="Y" sense="positive"
                      travelStart="0" travelEnd="120" travelUnit="mm">
        <warning id="wrn-050">Support the wheel. It is free once the skewer is withdrawn.</warning>
        <para>Lift the front wheel clear of the fork dropouts.</para>
      </proceduralStep>
    </mainProcedure>
  </procedure></content>
</dmodule>
"""

DM["DMC-SPOKE1-A-24-10-02-00A-720A-D"] = """<?xml version="1.0" encoding="UTF-8"?>
<!-- SURROGATE. Authored by Numberz.ai. Not Navy technical data. -->
<dmodule>
  <identAndStatusSection>
    <dmAddress>
      <dmIdent><dmCode modelIdentCode="SPOKE1" systemCode="24" subSystemCode="1"
        subSubSystemCode="0" assyCode="02" disassyCode="00" infoCode="720"/></dmIdent>
      <dmAddressItems><dmTitle><techName>Fender bolt</techName>
        <infoName>Install procedure</infoName></dmTitle></dmAddressItems>
    </dmAddress>
    <dmStatus><security securityClassification="01"/>
      <dataRestrictions>Distribution Statement A. Approved for public release.</dataRestrictions>
    </dmStatus>
  </identAndStatusSection>
  <content><procedure>
    <preliminaryRqmts>
      <reqSupportEquipDescrGroup>
        <supportEquipDescr id="tool-tw"><name>Torque wrench, 0 to 20 N.m</name></supportEquipDescr>
      </reqSupportEquipDescrGroup>
    </preliminaryRqmts>
    <mainProcedure>
      <proceduralStep id="stp-110" partRef="SPK-1500" motion="revolute" axis="Z" sense="positive"
                      travelStart="0" travelEnd="1080" travelUnit="deg"
                      toolRef="tool-tw" torque="5" torqueUnit="Nm">
        <caution id="cau-110">Do not exceed 5 N.m. The fender mount will strip.</caution>
        <para>Install the fender bolt and torque to 5 N.m.</para>
      </proceduralStep>
    </mainProcedure>
  </procedure></content>
</dmodule>
"""

DM["DMC-SPOKE1-A-24-10-00-00A-040A-D"] = """<?xml version="1.0" encoding="UTF-8"?>
<!-- SURROGATE. Authored by Numberz.ai. Not Navy technical data. -->
<dmodule>
  <identAndStatusSection>
    <dmAddress>
      <dmIdent><dmCode modelIdentCode="SPOKE1" systemCode="24" subSystemCode="1"
        subSubSystemCode="0" assyCode="00" disassyCode="00" infoCode="040"/></dmIdent>
      <dmAddressItems><dmTitle><techName>Front brake</techName>
        <infoName>Description</infoName></dmTitle></dmAddressItems>
    </dmAddress>
    <dmStatus><security securityClassification="01"/>
      <dataRestrictions>Distribution Statement A. Approved for public release.</dataRestrictions>
    </dmStatus>
  </identAndStatusSection>
  <content><description>
    <para>The front brake is a cable actuated dual pivot caliper. The brake lever rotates about
    the handlebar clamp axis through 42 degrees to its stop. Each caliper arm rotates inward
    through 12 degrees, carrying a brake pad onto the rim.</para>
    <articulationData>
      <joint partRef="SPK-1400" type="revolute" axis="X" lowerLimit="0" upperLimit="42" unit="deg"/>
      <joint partRef="SPK-1300" type="revolute" axis="Z" lowerLimit="0" upperLimit="12" unit="deg"/>
      <joint partRef="SPK-1301" type="revolute" axis="Z" lowerLimit="-12" upperLimit="0" unit="deg"/>
      <joint partRef="SPK-1200" type="continuous" axis="X" unit="deg"/>
      <joint partRef="SPK-1211" type="revolute" axis="Z" lowerLimit="0" upperLimit="180" unit="deg"/>
      <joint partRef="SPK-1212" type="continuous" axis="X" unit="deg"/>
      <joint partRef="SPK-1210" type="prismatic" axis="X" lowerLimit="0" upperLimit="150" unit="mm"/>
      <joint partRef="SPK-1500" type="continuous" axis="Z" unit="deg"/>
      <joint partRef="SPK-1100" type="continuous" axis="Y" unit="deg"/>
    </articulationData>
  </description></content>
</dmodule>
"""

def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "corpus", "s1000d")
    os.makedirs(out, exist_ok=True)
    for name, body in DM.items():
        with open(os.path.join(out, name + "_001-00_EN-US.XML"), "w", encoding="utf-8") as fh:
            fh.write(body)
    print("wrote %d surrogate data modules to %s" % (len(DM), out))

if __name__ == "__main__":
    main()
