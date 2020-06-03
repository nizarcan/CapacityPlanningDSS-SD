# CapacityPlanningDSS-SD
<p>This repository is the codebase of the 2019-2020 METU IE System Design project of team TC MANGO.
<br /><br />What this tool basically does is to fetch various data to process those data so that they can be 
used for the project's two-levelled capacity evaluation.<br /><br />The softwares used for mathematical 
programming and simulation are:</p>
<li>GAMS
<li>Arena Simulation

<h2>Classes</h2>
<ul>
<li>ArchivalDatabase: The class that are used to hold information and to be archived.
<li>OperationalSMInput: Lower-level operational simulation model's input system. This class' output goes  into Arena.
<li>OperationalMMInput: Lower-level operational mathematical programming model's input system. This class' output fed into GAMS.
<li>TacticalSMInput(Discontinued)
<li>TacticalMMInput: Upper-level tactical mathematical programming model's input system. This class' output fed into GAMS, just as OperationalMMInput.
</ul>
<br /><br /><br />
<h6>Repository created and maintained by Nizar Can, @nizarcan <small>Frontend template by Colorlib</small></h6>
