# ----------------------------- #
# Cell One. Step 1: Define Workspace, Variable Initialisation and create TWWHA layer #
# ----------------------------- #

#Ensure that the "overflights" (case sensitive layer name) feature layer is loaded to the project, along with the manually create required fields (Speed_KmMin, Perc_days_yr, Perc_7hr_day, Number_Flights_day). Alternative is to produce custom overflight layer with these parameters for other case study areas 
#Be aware that if the "overflights" layer is imported as a shapefile, the field names are limited by characters and may require manual editing to match script below. Store the layer as a gdb to avoid this issue.
#Ensure that the "Australia_2C_World_Heritage_Areas" is loaded to the project

import arcpy
import os
from arcpy.sa import *

# Set workspaces and geodatabase path
workspace = r"D:\DH_Wilderness\Project_layers\Soundscape_OSI_Dec_25\Dec_edit_v2\Dec_edit_v2.gdb"
arcpy.env.workspace = workspace
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(28355)  # GDA94 Zone 55
tempworkspace = r"D:\DH_Wilderness\Project_layers\Soundscape_OSI_Dec_25\Dec_edit_v2\temp.gdb"
if arcpy.Exists(tempworkspace):
    arcpy.Delete_management(tempworkspace)  # Delete existing GDB
arcpy.CreateFileGDB_management(os.path.dirname(tempworkspace), os.path.basename(tempworkspace))

print(f"Geodatabase {tempworkspace} has been cleared\n(if you need to keep it, be sure to save it elsewhere at the end prior to rerunning this code).")


# Ensure layers created are not automatically added to the map.
current_setting = arcpy.env.addOutputsToMap
arcpy.env.addOutputsToMap = False

# Correctly define the projection using SpatialReference and store as a constant
PROJECTION = arcpy.SpatialReference(28355)  # GDA94 Zone 55 (Note: this is chosen based on the current reliance on GDA94 for Tasmanian State datasets in theLIST etc.)

# Set environment variable
arcpy.env.outputCoordinateSystem = PROJECTION

# Verify that the projection is recognised
print("Output Coord Sys: "+ arcpy.env.outputCoordinateSystem.name)  # Should output 'GDA_1994_MGA_Zone_55'


# Vector Layer variables
input_layers = {
    "overflights": os.path.join(workspace, "overflights"),
    "Australia_2C_World_Heritage_Areas": os.path.join(workspace, "Australia_2C_World_Heritage_Areas"), 
}
layers = {
    "TWWHA": os.path.join(workspace, "TWWHA"), 
    "Overflights_allroutes_11kmbuff": os.path.join(workspace, "Overflights_allroutes_11kmbuff"),
    "TWWHA_11kmbuff": os.path.join(tempworkspace, "TWWHA_11kmbuff"),
    "Overflights_511buff_TWWHAclip": os.path.join(tempworkspace, "Overflights_511buff_TWWHAclip"),
    "TWWHA_audible_scale_Dissolve": os.path.join(tempworkspace, "TWWHA_audible_scale_Dissolve"),
    "Overflights_clip_TWWHA11km": os.path.join(tempworkspace, "Overflights_clip_TWWHA11km"),
    "Overflights_clip_TWWHA11km_GPA": os.path.join(tempworkspace, "Overflights_clip_TWWHA11km_GPA")
}

# Raster Layer variables
rasters = {
    "cumulative_total_AudDay_max": os.path.join(tempworkspace, "cumulative_total_AudDay_max"),
    "cumulative_total_AudDay_max_OSI": os.path.join(tempworkspace, "cumulative_total_AudDay_max_OSI"),
    "cumulative_days_per_yr": os.path.join(tempworkspace, "cumulative_days_per_yr"),
    "cumulative_highlow_noise": os.path.join(tempworkspace, "cumulative_highlow_noise"),
    "cumulative_audible": os.path.join(tempworkspace, "cumulative_audible"),
    "TWWHA_polygon_to_raster": os.path.join(tempworkspace, "TWWHA_polygon_to_raster"),
    "Percdaysyr_Combined_Frenchmans": os.path.join(tempworkspace, "Percdaysyr_Combined_Frenchmans"),
    "Percdaysyr_Combined_SCT": os.path.join(tempworkspace, "Percdaysyr_Combined_SCT"),
    "Percdaysyr_Combined_Central_Walls": os.path.join(tempworkspace, "Percdaysyr_Combined_Central_Walls"),
    "OSI_TWWHA": os.path.join(tempworkspace, "OSI_TWWHA"),
    "OSI": os.path.join(workspace, "OSI"),
    # The following raster layers are created in the code based on overflight or flight path and provided here to show the file name structure
    "Percdaysyr_{overflight}_PolygonToRaster": os.path.join(tempworkspace, "Percdaysyr_{overflight}_PolygonToRaster"),
    "Highnoise_{overflight}_PolygonToRaster": os.path.join(tempworkspace, "Highnoise_{overflight}_PolygonToRaster"),
    "Lownoise_{overflight}_PolygonToRaster": os.path.join(tempworkspace, "Lownoise_{overflight}_PolygonToRaster"),
    "Audible_{overflight}_PolygonToRaster": os.path.join(tempworkspace, "Audible_{overflight}_PolygonToRaster"),
    "{overflight}_HighLow": os.path.join(tempworkspace, "{overflight}_HighLow"),
    "Reclass_{overflight}_HighLow": os.path.join(tempworkspace, "Reclass_{overflight}_HighLow"),
    "{overflight}_PercYr":os.path.join(tempworkspace, "{overflight}_PercYr"),
    "Reclass_{overflight}_PercYr":os.path.join(tempworkspace, "Reclass_{overflight}_PercYr"),
    "{overflight}_Total_AudDay": os.path.join(tempworkspace, "{overflight}_Total_AudDay"),
    "{overflight}_Time_Minutes_Raster": os.path.join(tempworkspace, "{overflight}_Time_Minutes_Raster"),
    "Reclass_{overflight}_Total_AudDay": os.path.join(tempworkspace, "Reclass_{overflight}_Total_AudDay"),
    "GPA_{overflight}_11km_ToRaster": os.path.join(tempworkspace, "GPA_{overflight}_11km_ToRaster"),
    "EucDist_{overflight}_11km": os.path.join(tempworkspace, "EucDist_{overflight}_11km"),
    "EucDist_{overflight}_JKcurve": os.path.join(tempworkspace, "EucDist_{overflight}_JKcurve"),
    "EucDist_{overflight}_JKcurve_Con": os.path.join(tempworkspace, "EucDist_{overflight}_JKcurve_Con"),   
    "OSI_{overflight}": os.path.join(workspace, "OSI_{overflight}"),
    "Sum_Total_AudDay_SCT": os.path.join(tempworkspace, "Sum_Total_AudDay_SCT"),
    "Sum_Total_AudDay_Frenchmans": os.path.join(tempworkspace, "Sum_Total_AudDay_Frenchmans"),
    "Sum_Total_AudDay_Walls": os.path.join(tempworkspace, "Sum_Total_AudDay_Walls"),
    # New Dec_25: no mask capped decay raster for sensitivity testing
    "EucDist_{overflight}": os.path.join(tempworkspace, "EucDist_{overflight}"),
    "EucDist_{overflight}_TWWHA": os.path.join(tempworkspace, "EucDist_{overflight}_TWWHA"),
    "SlantDist_{overflight}_TWWHA": os.path.join(tempworkspace, "SlantDist_{overflight}_TWWHA"),
    "SlantNoise_{of}_TWWHA": os.path.join(tempworkspace, "SlantNoise_{of}_TWWHA"),
    "SlantNoise_{overflight}_TWWHA": os.path.join(tempworkspace, "SlantNoise_{overflight}_TWWHA")
}

                                       
# Attribute Table Flight Characteristics: *Fields Manually created in overflights layer at step one, manually populate attribute values at step one
flight_characteristics = {
    "Speed_KmMin": "Assumed flight speed (Km/Minute)",
    "Perc_days_yr": "Percent days per year operations",
    "Perc_7hr_day": "Percent operational day (assumed 7-hour day)",
    "Number_flights_day": "Number of flights per day"
}

# Attribute Table OSI Scoring Variables (Only OSI fields)
osi_scoring = {
    "Audibility_Score": "Applies to 0m-11000m buffer areas",
    "Daily_Score": "≥25 = -1, <25 = 0",
    "Annual_score": ">75 = -1, 25-75 = 0, <25 = 1",
    "High_Noise_Score": "Applies to ≤5000m buffer area",
    "Low_Noise_Score": "Applies to >5000m – 11000m buffer area",
    "Total_OSI_Score": "Final computed OSI score",
    "Area_Ha": "Total Area (Hectare)"  
}

# List of overflight names that exist in input_layers["overflights"]
overflights = ["PWS_SC_Track_ingress", "PWS_SC_Track_maintenance", "Par_Avion_PWS_Melalueca", 
               "Central_Walls_ingress", "Central_Walls", "Frenchmans_ingress", "Frenchmans_Cap", "Maatsuyker", "Overland_Track"]

# List to store failed overflights
skipped_overflights = []

# END Variables

print("\n✅ Cell One complete: Workspace and variables initialised.")
print(f"  Workspace: {workspace}")
print(f"  Temporary GDB: {tempworkspace}")
print(f"  Number of overflights: {len(overflights)}")
print(f"  Projection set to: {PROJECTION.name}")
print(f"  Key raster layers defined: {len(rasters)}")
print(f"  Key vector layers defined: {len(layers)}")


#Ensure "overflights" layer is located in GDB, and added to Map

# Calculate 'Length' field geometry for 'Overflights'
arcpy.management.CalculateGeometryAttributes(input_layers["overflights"], [["length", "LENGTH"]], "KILOMETERS")

# Make a TWWHA feature layer from the input
arcpy.management.MakeFeatureLayer(input_layers["Australia_2C_World_Heritage_Areas"], "Australia_WHA_Layer")

# Select the Tasmanian Wilderness
arcpy.management.SelectLayerByAttribute("Australia_WHA_Layer", "NEW_SELECTION", "NAME = 'Tasmanian Wilderness'")

# Copy the selected feature to a new feature class
layers["TWWHA"] = arcpy.management.CopyFeatures("Australia_WHA_Layer", layers["TWWHA"])[0]



# ----------------------------- #
# Step 2: Apply assumptions (source noise level (dBA@1m), atmospheric absorption),
# determine high noise >= 35 dBA and audibility threshold (set to 20dBA).
# TWWHA mask applied immediately after Euclidean Distance
# ----------------------------- #

# -------------------------------------------------------------------
# Setup
# -------------------------------------------------------------------

arcpy.CheckOutExtension("Spatial")

#workspace = r"D:\DH_Wilderness\Project_layers\Soundscape_OSI_Dec_25\Dec_edit_v2\Dec_edit_v2.gdb"
#tempworkspace = r"D:\DH_Wilderness\Project_layers\Soundscape_OSI_Dec_25\Dec_edit_v2\temp.gdb"

arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = None

# List of overflight names that exist in input_layers["overflights"]
overflights = [
    "PWS_SC_Track_ingress",
    "PWS_SC_Track_maintenance",
    "Par_Avion_PWS_Melalueca",
    "Central_Walls_ingress",
    "Central_Walls",
    "Frenchmans_ingress",
    "Frenchmans_Cap",
    "Maatsuyker",
    "Overland_Track"
]

# -------------------------------------------------------------------
# Ensure overflights feature layer exists
# -------------------------------------------------------------------

arcpy.management.MakeFeatureLayer(
    os.path.join(workspace, "overflights"),
    "overflights"
)

# TWWHA feature to use as mask
twwha_layer = os.path.join(workspace, "TWWHA")

# -------------------------------------------------------------------
# Loop over overflight routes
# -------------------------------------------------------------------

for of in overflights:

    print(f"\nProcessing overflight: {of}")

    # ---------------------------------------------------------------
    # 1. Select overflight route
    # ---------------------------------------------------------------
    arcpy.management.SelectLayerByAttribute(
        "overflights",
        "NEW_SELECTION",
        f"Overflight_Name = '{of}'"
    )

    if int(arcpy.management.GetCount("overflights")[0]) == 0:
        print(f"  ⚠ No features found for {of}, skipping.")
        continue

    # ---------------------------------------------------------------
    # 2a. Set analysis extent
    # ---------------------------------------------------------------
    arcpy.env.extent = arcpy.Describe(
        os.path.join(workspace, "TWWHA")
    ).extent

    # ---------------------------------------------------------------
    # 2b. Euclidean Distance (FULL geometry) capped at 35000metres
    # ---------------------------------------------------------------
    euc_name = os.path.join(tempworkspace, f"EucDist_{of}")
    euc_raster = EucDistance("overflights", 35000, 50, None, "PLANAR")
    euc_raster.save(euc_name)

    # ---------------------------------------------------------------
    # 2c. Mask Euclidean Distance to TWWHA
    # ---------------------------------------------------------------
    euc_raster = Raster(euc_name)
    euc_twwha = ExtractByMask(euc_raster, twwha_layer)

    euc_twwha_name = os.path.join(tempworkspace, f"EucDist_{of}_TWWHA")
    euc_twwha.save(euc_twwha_name)

    # ---------------------------------------------------------------
    # 2d. Slant Distance (Euclidean + altitude)
    # ---------------------------------------------------------------
    altitude_m = 250 # select constant altitude level (m AGL)

    euc_twwha = Raster(euc_twwha_name)

    slant_raster = SquareRoot(
        (euc_twwha * euc_twwha) + (altitude_m * altitude_m)
    )

    slant_name = os.path.join(tempworkspace, f"SlantDist_{of}_TWWHA")
    slant_raster.save(slant_name)

    print(f"  ✔ Slant distance raster created")

    # ---------------------------------------------------------------
    # 2e. Noise Propagation (from slant distance)
    # ---------------------------------------------------------------
    L_ref = 115.0     # dBA @ 1 m
    r_ref = 1.0       # meters
    atm_att = 0.001  # dB per meter (ISO ~250 Hz)

    slant_raster = Raster(slant_name)

    noise_raster = (
        L_ref
        - (20 * Log10(slant_raster / r_ref))
        - (atm_att * (slant_raster - r_ref))
    )

    noise_name = os.path.join(tempworkspace, f"SlantNoise_{of}_TWWHA")
    noise_raster.save(noise_name)

    print(f"  ✔ Noise raster created")

    # ---------------------------------------------------------------
    # 2f. Report Noise Distance Thresholds
    # ---------------------------------------------------------------
    noise_raster = Raster(noise_name)
    euc_raster = Raster(euc_twwha_name)
    
       
    # ---- 55 dBA audibile distance ----
    noise_55 = SetNull(noise_raster < 55, euc_raster)
    dist_55 = arcpy.management.GetRasterProperties(
        noise_55, "MAXIMUM"
    )[0]

    # ---- 35 dBA high noise distance ----
    noise_35 = SetNull(noise_raster < 35, euc_raster)
    dist_35 = arcpy.management.GetRasterProperties(
        noise_35, "MAXIMUM"
    )[0]

    # ---- 20 dBA audibile distance ----
    noise_20 = SetNull(noise_raster < 20, euc_raster)
    dist_20 = arcpy.management.GetRasterProperties(
        noise_20, "MAXIMUM"
    )[0]

    print(f"  🔊 {of}")
    print(f"     55 dBA distance: {float(dist_55):,.0f} m")
    print(f"     35 dBA distance: {float(dist_35):,.0f} m")
    print(f"     20 dBA distance: {float(dist_20):,.0f} m")

# -------------------------------------------------------------------
# Cleanup
# -------------------------------------------------------------------

arcpy.management.SelectLayerByAttribute("overflights", "CLEAR_SELECTION")
arcpy.env.extent = None

print("\nAll overflights processed successfully.")
print("TWWHA mask applied immediately after Euclidean Distance.")



# ----------------------------- #
# Step 3: Vector Layer Processing - this cell produces Individual OSI Scores for each overflight, which are then stored in the attribute table #
# ----------------------------- #

#History of this script: this was originally written using fixed buffers of 5km (representing High Noise threshold of 35dBA) 
#and 11km (representing audibility threshold set at 20dBA as per associated paper). Step 2 (previous cell) now provides differing variables dependant on assumptions.
#This means that the users has to manually set the 35dBA distance and audibility distances manually below, replacing te previous 5km and 11km distances,
#The layer names have remained as original to preserve the functionality of the script

##Apply distance assumptions below for audibility (eg 20dBA @ 11km) and high/low noise threshold distance derived from rasters 
##in previous step (eg audibility @ 13556m, 35dBA @ 2719 metres)
##This step (script cell) is implemented using basic overflight and audibility assumptions in the absence of 
##specialised overflight noise modelling software outputs 

print("Vector layer processing started.")

# Create TWWHA buffer (Insert audible distance - ignore references to 11km and insert audible distance manually) #----
arcpy.analysis.Buffer(layers["TWWHA"], layers["TWWHA_11kmbuff"], dist_20+" Meters", "FULL", "ROUND", "NONE", None, "PLANAR")

# Clip Overflights with TWWHA 11km buffer
arcpy.analysis.Clip(input_layers["overflights"], layers["TWWHA_11kmbuff"], layers["Overflights_clip_TWWHA11km"], None)

# Calculate audible flight path length
arcpy.management.CalculateGeometryAttributes(layers["Overflights_clip_TWWHA11km"], [["length", "LENGTH"]], "KILOMETERS")

# Properly reference the in_memory workspace
buf0_path = os.path.join("in_memory", "buf0")

# Check if the feature class exists before attempting to delete
if arcpy.Exists(buf0_path):
    arcpy.Delete_management(buf0_path)

# Buffer Overflights by 5km and 11km #----INSERT 35dBA and audibility DISTANCES FROM STEP 2#
arcpy.analysis.MultipleRingBuffer(input_layers["overflights"], layers["Overflights_allroutes_11kmbuff"], [float(dist_35), float(dist_20)], "Meters", "Buf_distance", "NONE", "FULL")

# Clip buffered overflights with TWWHA to get audible footprints
arcpy.analysis.Clip(layers["Overflights_allroutes_11kmbuff"], layers["TWWHA"], layers["Overflights_511buff_TWWHAclip"], None)

# A re-occurring fault leads to a space being inserted after the Maatsuyker overflight name. Strip leading/trailing spaces from the Overflight_Name field
with arcpy.da.UpdateCursor(layers["Overflights_511buff_TWWHAclip"], ["Overflight_Name"]) as cursor:
    for row in cursor:
        row[0] = row[0].strip()  # Remove spaces
        cursor.updateRow(row)

print("Stripped spaces from Overflight_Name field in Overflights_511buff_TWWHAclip.")

#-----------------#
#Adding OSI Fields#
#-----------------#

for field in osi_scoring.keys():
    try:
        # Ensure valid field names
        valid_field_name = field.replace(" ", "_").replace("-", "_")

        # Check if field already exists
        existing_fields = [f.name for f in arcpy.ListFields(layers["Overflights_511buff_TWWHAclip"])]
        if valid_field_name not in existing_fields:
            arcpy.management.AddField(layers["Overflights_511buff_TWWHAclip"], valid_field_name, "DOUBLE")
            print(f"Added field: {valid_field_name}")
        else:
            print(f"Field '{valid_field_name}' already exists. Skipping.")

    except Exception as e:
        print(f"Error adding field {valid_field_name}: {e}")

# ----------------------------- #
# OSI Calculations
# ----------------------------- #

## Create (x6) new fields for the OSI scores.
## “Audibility_Score”, “Daily_Score”, “Annual_score”, “High_Noise_Score”, “Low_Noise_Score”, “Total_OSI_Score”

# Assign audibility score
arcpy.management.CalculateField(layers["Overflights_511buff_TWWHAclip"], "Audibility_Score", "-1", "PYTHON3")

# Assign daily score based on "Perc_7hr_day"
arcpy.management.CalculateField(
    layers["Overflights_511buff_TWWHAclip"],
    "Daily_Score",
    "-1 if !Perc_7hr_day! >= 25 else 0",
    "PYTHON3"
)

# Assign annual score based on "Perc_days_yr"
arcpy.management.CalculateField(
    layers["Overflights_511buff_TWWHAclip"],
    "Annual_score",
    "-1 if !Perc_days_yr! > 75 else (0 if !Perc_days_yr! > 25 else 1)",
    "PYTHON3"
)

# Clear any previous selection
arcpy.management.SelectLayerByAttribute(layers["Overflights_511buff_TWWHAclip"], "CLEAR_SELECTION")

# Make a feature layer from the feature class
arcpy.management.MakeFeatureLayer(
    layers["Overflights_511buff_TWWHAclip"],
    "Overflights_Layer"
)
# Clear any previous selection
arcpy.management.SelectLayerByAttribute("Overflights_Layer", "CLEAR_SELECTION")

# Create a feature layer so selection works properly
arcpy.management.MakeFeatureLayer(
    layers["Overflights_511buff_TWWHAclip"],
    "Overflights_Layer"
)

# --- Assign -1 to 35dBa distance threshold buffers --- CHANGE TO SUIT
arcpy.management.SelectLayerByAttribute("Overflights_Layer", "NEW_SELECTION", "Buf_distance = "+dist_35)
arcpy.management.CalculateField("Overflights_Layer", "High_Noise_Score", "-1", "PYTHON3")

# --- Assign 0 to everything else --- CHANGE TO SUIT
arcpy.management.SelectLayerByAttribute("Overflights_Layer", "NEW_SELECTION", "Buf_distance <> "+dist_35)
arcpy.management.CalculateField("Overflights_Layer", "High_Noise_Score", "0", "PYTHON3")

# Repeat for Low_Noise_Score audibility distance
arcpy.management.SelectLayerByAttribute("Overflights_Layer", "NEW_SELECTION", "Buf_distance = "+dist_20)
arcpy.management.CalculateField("Overflights_Layer", "Low_Noise_Score", "0", "PYTHON3")

arcpy.management.SelectLayerByAttribute("Overflights_Layer", "NEW_SELECTION", "Buf_distance <> "+dist_20)
arcpy.management.CalculateField("Overflights_Layer", "Low_Noise_Score", "0", "PYTHON3")  

# Clear selection just to be tidy
arcpy.management.SelectLayerByAttribute(layers["Overflights_511buff_TWWHAclip"], "CLEAR_SELECTION")

# Compute Total OSI Scores for (i) High Noise areas, and (ii) Low Noise areas (Max quality score is 5)

# Step 0: Create a feature layer so selections work properly
arcpy.management.MakeFeatureLayer(
    layers["Overflights_511buff_TWWHAclip"],
    "Overflights_Layer"
)

# Step 1: Compute Total OSI Score for HIGH NOISE buffers (insert distance)
arcpy.management.SelectLayerByAttribute(
    "Overflights_Layer",
    "NEW_SELECTION",
    "Buf_distance = "+dist_35
)
arcpy.management.CalculateField(
    "Overflights_Layer",
    "Total_OSI_Score",
    "5 + (!Annual_score!) + (!Daily_Score!) + (!High_Noise_Score!) + (!Audibility_Score!)",
    "PYTHON3"
)

# Step 2: Compute Total OSI Score for audibility distance buffers (insert distance)
arcpy.management.SelectLayerByAttribute(
    "Overflights_Layer",
    "NEW_SELECTION",
    "Buf_distance = "+dist_20
)
arcpy.management.CalculateField(
    "Overflights_Layer",
    "Total_OSI_Score",
    "5 + (!Annual_score!) + (!Daily_Score!) + (!Low_Noise_Score!) + (!Audibility_Score!)",
    "PYTHON3"
)

# Step 3: Optional — clear selection afterward
arcpy.management.SelectLayerByAttribute(
    "Overflights_Layer",
    "CLEAR_SELECTION"
)

# Calculate area in hectares
arcpy.management.CalculateGeometryAttributes(layers["Overflights_511buff_TWWHAclip"], [["Area_Ha", "AREA"]], area_unit="HECTARES")

print("Overflight vector generation completed.")
print("Workspace:", arcpy.env.workspace)
print("Temp workspace exists:", arcpy.Exists(tempworkspace))
print("Overflights exists:", arcpy.Exists(input_layers["overflights"]))
print("TWWHA exists:", arcpy.Exists(layers["TWWHA"]))


# ----------------------------- #
# Step 4. Raster Processing part 1 of 3. Layers further developed to produce cumulative impact details. 
# This script applies day per yr rasters, high / low noise rasters (binary y/n), audible rasters (binary y/n) #
# ----------------------------- #

print("Overflight raster generation part 1 of 3 started.")

#--Create Percent days year rasters---#

# Convert polygon to raster for days per year impact
#----MANUALLY INSERT 35dBA threshold distance from Step 2, and audibility distance from step 2---

for overflight in overflights:
    expression = f"Buf_distance = {dist_20} And Overflight_Name = '{overflight}'"
    selection = arcpy.management.SelectLayerByAttribute(layers["Overflights_511buff_TWWHAclip"], "NEW_SELECTION", expression)
    output_raster = rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight=overflight)
    arcpy.conversion.PolygonToRaster(selection, "Perc_days_yr", output_raster, "CELL_CENTER", "NONE", 50)


# Reclassify days per year rasters
reclass_rules = "0 25 1;25.000010 75 0;75.000100 100 -1;NODATA 0"
for overflight in overflights:
    input_raster = rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight=overflight)
    output_raster = rasters["Reclass_{overflight}_PercYr"].format(overflight=overflight)
    out_raster = Reclassify(input_raster, "VALUE", reclass_rules, "NODATA")
    out_raster.save(output_raster)
    
# Merge SCT overflight layers (x2) using Cell Statistics (MAX)
# Ensure input rasters are retrieved correctly from the 'rasters' dictionary
input_rasters = [
    rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight="PWS_SC_Track_maintenance"),
    rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight="PWS_SC_Track_ingress")
]

# Check if rasters exist before running CellStatistics
for raster in input_rasters:
    print(f"Checking: {raster} -> Exists: {arcpy.Exists(raster)}")

# If all rasters exist, proceed with CellStatistics
if all(arcpy.Exists(raster) for raster in input_rasters):
    with arcpy.EnvManager(outputCoordinateSystem=PROJECTION):
        out_raster = arcpy.ia.CellStatistics(";".join(input_rasters), "MAXIMUM", "DATA", "SINGLE_BAND")
        out_raster.save(rasters["Percdaysyr_Combined_SCT"])
else:
    print("Error: One or more input rasters for SCT do not exist. Check the file paths.")

# Merge Central Walls overflight layers (x2) using Cell Statistics (MAX)
# Ensure input rasters are retrieved correctly from the 'rasters' dictionary
input_rasters = [
    rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight="Central_Walls"),
    rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight="Central_Walls_ingress")
]

# Check if rasters exist before running CellStatistics
for raster in input_rasters:
    print(f"Checking: {raster} -> Exists: {arcpy.Exists(raster)}")

# If all rasters exist, proceed with CellStatistics
if all(arcpy.Exists(raster) for raster in input_rasters):
    with arcpy.EnvManager(outputCoordinateSystem=PROJECTION):
        out_raster = arcpy.ia.CellStatistics(";".join(input_rasters), "MAXIMUM", "DATA", "SINGLE_BAND")
        out_raster.save(rasters["Percdaysyr_Combined_Central_Walls"])
else:
    print("Error: One or more input rasters for Central Walls do not exist. Check the file paths.")


# Merge Frenchmans overflight layers (x2) using Cell Statistics (MAX)
# Ensure input rasters are retrieved correctly from the 'rasters' dictionary
input_rasters = [
    rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight="Frenchmans_ingress"),
    rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight="Frenchmans_Cap")
]

# Check if rasters exist before running CellStatistics
for raster in input_rasters:
    print(f"Checking: {raster} -> Exists: {arcpy.Exists(raster)}")

# If all rasters exist, proceed with CellStatistics
if all(arcpy.Exists(raster) for raster in input_rasters):
    with arcpy.EnvManager(outputCoordinateSystem=PROJECTION):
        out_raster = arcpy.ia.CellStatistics(";".join(input_rasters), "MAXIMUM", "DATA", "SINGLE_BAND")
        out_raster.save(rasters["Percdaysyr_Combined_Frenchmans"])
else:
    print("Error: One or more input rasters for Frenchmans do not exist. Check the file paths.")


# Merge the above three rasters with the three remaining “Perc_days_yr” rasters (Sum)
remaining_rasters = [
    rasters["Percdaysyr_Combined_Frenchmans"],
    rasters["Percdaysyr_Combined_Central_Walls"],
    rasters["Percdaysyr_Combined_SCT"],
    rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight="Maatsuyker"),
    rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight="Overland_Track"),
    rasters["Percdaysyr_{overflight}_PolygonToRaster"].format(overflight="Par_Avion_PWS_Melalueca")
]

with arcpy.EnvManager(outputCoordinateSystem=PROJECTION):
    out_raster = arcpy.ia.CellStatistics(";".join(remaining_rasters), "SUM", "DATA", "SINGLE_BAND")
    out_raster.save(rasters["cumulative_days_per_yr"])

# Reclassify the merged raster using the Decision Tree
reclass_rules = "0 25 1;25.000010 75 0;75.000100 100 -1;NODATA 0"

with arcpy.EnvManager(outputCoordinateSystem=PROJECTION):
    out_raster = arcpy.sa.Reclassify(rasters["cumulative_days_per_yr"], "VALUE", reclass_rules, "NODATA")
    out_raster.save(rasters["cumulative_days_per_yr"])

print("Completed cumulative_days_per_yr raster")

# Create High and Low noise raster layers#
# -------------------------------
# High Noise Rasters for Individual Overflights# - WARNING, manually input 35dBa distance threshold below, 
# to match distance derived at Step 2
# -------------------------------
print("Processing High Noise Rasters...")

for overflight in overflights:
    expression = f"Buf_distance = {dist_35} AND Overflight_Name = '{overflight}'"
    selection = arcpy.management.SelectLayerByAttribute(layers["Overflights_511buff_TWWHAclip"], "NEW_SELECTION", expression)
    
    # Define output raster path
    output_raster = rasters["Highnoise_{overflight}_PolygonToRaster"].format(overflight=overflight)
    
    # Convert selected polygons to raster
    arcpy.conversion.PolygonToRaster(
        selection, "High_Noise_Score", 
        output_raster, "CELL_CENTER", "NONE", 50
    )
    print(f" Highnoise_{overflight}_PolygonToRaster created successfully.")
    
print(" Highnoise_{overflight}_PolygonToRaster for each overflight Created Successfully.")

# -------------------------------
# Low Noise Rasters for Individual Overflights. Manually insert audbility distance from Step 2
# -------------------------------
print("Processing Low Noise Rasters...")

for overflight in overflights:
    expression = f"Buf_distance = {dist_20} AND Overflight_Name = '{overflight}'"
    selection = arcpy.management.SelectLayerByAttribute(layers["Overflights_511buff_TWWHAclip"], "NEW_SELECTION", expression)
    
    # Define output raster path
    output_raster = rasters["Lownoise_{overflight}_PolygonToRaster"].format(overflight=overflight)
    
    # Convert selected polygons to raster
    arcpy.conversion.PolygonToRaster(
        selection, "Low_Noise_Score", 
        output_raster, "CELL_CENTER", "NONE", 50
    )
    print(f" Lownoise_{overflight}_PolygonToRaster created successfully.")

print(" Lownoise_{overflight}_PolygonToRaster for each overflight created successfully.")

# -------------------------------
# Merge Individual High & Low Noise Rasters Per Overflight
# -------------------------------
print("Processing Individual High/Low Noise Merges...")


from arcpy.sa import Con, IsNull, Raster

for overflight in overflights:
    high_raster = rasters["Highnoise_{overflight}_PolygonToRaster"].format(overflight=overflight)
    low_raster = rasters["Lownoise_{overflight}_PolygonToRaster"].format(overflight=overflight)
    
    if arcpy.Exists(high_raster) and arcpy.Exists(low_raster):
        combined_raster_path = rasters["{overflight}_HighLow"].format(overflight=overflight)

        # Load rasters
        high = Raster(high_raster)
        low = Raster(low_raster)

        # Replace NoData with 0
        high_fixed = Con(IsNull(high), 0, high)
        low_fixed = Con(IsNull(low), 0, low)

        # Combine rasters
        combined_raster = high_fixed + low_fixed
        combined_raster.save(combined_raster_path)

        if not arcpy.Exists(combined_raster_path):
            print(f" Warning: Failed to create HighLow Noise raster: {combined_raster_path}. Skipping overflight: {overflight}...")
        else:
            print(f" Combined High/Low Noise Raster Created: {combined_raster_path}")
    else:
        skipped_overflights.append(overflight)
        if not arcpy.Exists(high_raster):
            print(f" Warning: Missing high noise raster: {high_raster}. Skipping overflight: {overflight}...")
        else:
            print(f" Warning: Missing low noise raster: {low_raster}. Skipping overflight: {overflight}...")

# -------------------------------
# Reclassify Individual High/Low Noise Rasters
# -------------------------------
print("Processing Reclassification of High/Low Noise Rasters...")

reclass_rules = "-1 -1;0 0"  # Only define valid values; unlisted values become NoData

for overflight in overflights:
    input_raster = rasters["{overflight}_HighLow"].format(overflight=overflight)

    if arcpy.Exists(input_raster):
        output_raster = rasters["Reclass_{overflight}_HighLow"].format(overflight=overflight)

        # Perform reclassification, preserving NoData
        out_raster = Reclassify(input_raster, "VALUE", reclass_rules, "NODATA")
        out_raster.save(output_raster)

        if not arcpy.Exists(output_raster):
            print(f" Warning: Failed to create Reclassified HighLow Noise raster: {output_raster}. Skipping overflight: {overflight}...")
        else:
            print(f" Reclassified Raster Created: {output_raster}")
    else:
        skipped_overflights.append(overflight)
        print(f" Warning: Missing input raster for {overflight}. Skipping...")

# -------------------------------
# Merge All Reclassified High/Low Noise Rasters to create cumulative raster using Min to show max impact
# -------------------------------
print("Processing Final Cumulative High/Low Noise Raster...")

valid_rasters = [rasters["Reclass_{overflight}_HighLow"].format(overflight=overflight) for overflight in overflights if arcpy.Exists(rasters["Reclass_{overflight}_HighLow"].format(overflight=overflight))]

if valid_rasters:
    cumulative_highlow_noise = CellStatistics(valid_rasters, "MINIMUM", "DATA")
    cumulative_highlow_noise.save(rasters["cumulative_highlow_noise"])
    print(f" Final Cumulative High/Low Noise Raster Created: {rasters['cumulative_highlow_noise']}")
else:
    print(" Warning: No valid rasters found for final cumulative merge.")

          
#------------------------#
#Create Audible rasters# MANUALLY INSERT audibility distance from Step 2
#------------------------#

# Convert polygons to rasters for audible areas
for overflight in overflights:
    expression = f"Buf_distance = {dist_20} And Overflight_Name = '{overflight}'"
    selection = arcpy.management.SelectLayerByAttribute(layers["Overflights_511buff_TWWHAclip"], "NEW_SELECTION", expression)
    output_raster = os.path.join(tempworkspace, rasters["Audible_{overflight}_PolygonToRaster"].format(overflight=overflight))
    arcpy.conversion.PolygonToRaster(selection, "Audibility_Score", output_raster, "CELL_CENTER", "NONE", 50)

# Merge audible area rasters
audible_rasters = [rasters["Audible_{overflight}_PolygonToRaster"].format(overflight=overflight) for overflight in overflights]
out_audible = CellStatistics(audible_rasters, "MAXIMUM", "DATA")
out_audible.save(rasters["cumulative_audible"])
                         

# Reclassify cumulative audible raster
out_reclass_audible = Reclassify(rasters["cumulative_audible"], "VALUE", "-1 -1;NODATA 0", "NODATA")
out_reclass_audible.save(rasters["cumulative_audible"])

print("Raster processing and reclassification part 1 of 3 completed.")
#END Raster Part One of three





# ----------------------------- #
# Step 5. Raster layer processing part 2 of 3: Apply the time audible rasters and the 'JKCurve' . The 'JKCurve' formula (polynomial approach) was emperically derived 
# and applied to predict the proportion of time that a point (raster cell) away from the direct overflight path was exposed to overflight noise from one flight; 
# the application of the formula via the ArcGIS process provided each raster cell with a value which was then divided by the average predicted overflight speed 
# to provide an audibility (time) value at each raster cell. Originally audibility distance was 11km, but the formula has sinced been modified to enable its use
# with differing audibility distances by scaling to the chosen audibility distance

# ----------------------------- #
import arcpy
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# -------------------------------------------------------------------
# PARAMETERS
# -------------------------------------------------------------------
R0 = 11.0       # Original calibration radius (km)
Rtest = float(dist_20)/1000    # New test radius (km)

print("Overflight raster generation part 2 of 3 started.")

# -------------------------------------------------------------------
# STEP 1: Apply polynomial decay to existing TWWHA Euclidean rasters
# -------------------------------------------------------------------

#Set analysis extent for consistency
arcpy.env.extent = arcpy.Describe(layers["TWWHA_11kmbuff"]).extent

for overflight in overflights:
    # Use existing masked Euclidean raster
    input_path = rasters["SlantDist_{overflight}_TWWHA"].format(overflight=overflight)

    if arcpy.Exists(input_path):
        input_raster = Raster(input_path)
        input_raster_km = input_raster / 1000  # convert to km

        # -----------------------------------------------------------
        # Curve emperically derived, based on 11km and re-scaled 
        # -----------------------------------------------------------
        x = input_raster_km / Rtest            # normalise to test radius
        FROM_equiv = x * R0                     # convert to 11 km-equivalent distance

        ALONG_equiv = (
            21.90
            - 0.7624 * FROM_equiv
            + 0.08159 * (FROM_equiv ** 2)
            - 0.01845 * (FROM_equiv ** 3)
        )

        ALONG_test = ALONG_equiv * (Rtest / R0)  # rescale for test radius

        # Apply audibility limit
        output_raster = Con(input_raster_km <= Rtest, ALONG_test, 0)

        # Save the new audibility time decay raster
        output_path = rasters.get("EucDist_{overflight}_JKcurve_13km",
                                  os.path.join(tempworkspace, f"EucDist_{overflight}_JKcurve_13km")).format(overflight=overflight)
        output_raster.save(output_path)

        print(f" Noise time decay applied and saved for: {overflight}")
    else:
        print(f"Warning: Distance raster missing for {overflight}. Skipping decay.")

print("All noise time decay calculations complete.")

# -------------------------------------------------------------------
# STEP 2: Remove negative values in decay raster
# -------------------------------------------------------------------
for overflight in overflights:
    input_path = os.path.join(tempworkspace, f"EucDist_{overflight}_JKcurve_13km")
    if arcpy.Exists(input_path):
        input_raster = Raster(input_path)
        output_raster = Con(input_raster < 0, 0, input_raster)
        output_raster.save(os.path.join(tempworkspace, f"EucDist_{overflight}_JKcurve_Con"))
        print(f" Negative values clipped for: {overflight}")
    else:
        print(f"Warning: Decay raster missing for {overflight}. Skipping clipping.")

print("All negative value clipping complete")



#-----Start AudDay raster processing#    
    
arcpy.management.SelectLayerByAttribute("Australia_2C_World_Heritage_Areas", "NEW_SELECTION", "NAME = 'Tasmanian Wilderness'", None)


# Ensure "Overflights_511buff_TWWHAclip_Layer" exists THIS WILL USE THE BUFFER LAYER PREVIOSULY CREATED (may differ from 11km)
overflights_layer = layers["Overflights_511buff_TWWHAclip"]
if not arcpy.Exists(overflights_layer):
    raise RuntimeError(f"Layer '{overflights_layer}' does not exist in {tempworkspace}. Check earlier steps.")

    
# Step 1: Calculate Time Per Day Audible for Each Overflight
for flight_path in overflights:
    try:
        # Select the correct flight path in Overflights_511buff_TWWHAclip_Layer ---- #set value for SENSITIVITY testing # INSERT AUDIBILITY DISTANCE FROM STEP 2
        arcpy.management.SelectLayerByAttribute(overflights_layer, "NEW_SELECTION", f"Overflight_Name = '{flight_path}' AND Buf_distance = {dist_20}")

        # Extract Speed_KmMin from the attribute table
        speed_km_min = None
        with arcpy.da.SearchCursor(overflights_layer, ["Overflight_Name", "Speed_KmMin"]) as cursor:
            for row in cursor:
                if row[0] == flight_path:
                    speed_km_min = row[1]
                    break

        if speed_km_min is None:
            raise ValueError(f"Speed_KmMin value for '{flight_path}' not found.")

        # Define input raster
        input_raster = Raster(rasters["EucDist_{overflight}_JKcurve_Con"].format(overflight=flight_path))

        # Compute time in minutes per flight
        output_raster = input_raster / speed_km_min
        output_raster_path = rasters["{overflight}_Time_Minutes_Raster"].format(overflight=flight_path)
        output_raster.save(output_raster_path)

        print(f" Calculated Time Per Overflight for {flight_path} - Saved: {output_raster_path}")

    except Exception as e:
        print(f"Error processing {flight_path}: {str(e)}")

print("Completed time calculations for all overflights.")


# Step 2: Multiply Time Raster by Number of Flights Per Day
for flight_path in overflights:
    try:
        # Select the correct overflight name #WARNING SET AUDIBILITY DISTANCE FROM STEP 2#
        selection = arcpy.management.SelectLayerByAttribute(overflights_layer, "NEW_SELECTION", f"Overflight_Name = '{flight_path}' AND Buf_distance = {dist_20}")

        # Extract Number_flights_day from the attribute table
        num_flights_day = None
        with arcpy.da.SearchCursor(selection, ["Overflight_Name", "Number_flights_day"]) as cursor:
            for row in cursor:
                if row[0] == flight_path:
                    num_flights_day = row[1]
                    break

        if num_flights_day is None:
            raise ValueError(f"Number_flights_day value for '{flight_path}' not found.")

        # Define input raster
        input_raster = Raster(rasters["{overflight}_Time_Minutes_Raster"].format(overflight=flight_path))

        # Compute total minutes audible per day
        output_raster = input_raster * num_flights_day
        output_raster_path = rasters["{overflight}_Total_AudDay"].format(overflight=flight_path)
        output_raster.save(output_raster_path)

        print(f" Calculated Total Audible Minutes per Day for {flight_path} - Saved: {output_raster_path}")

    except Exception as e:
        print(f"Error processing audibility for {flight_path}: {str(e)}")

print("Completed total audibility calculations for all overflights.")

# Step 3: Reclassify Total AudDay Rasters
reclass_rules = "0 104.190788 0;105 420 -1;NODATA 0"

for flight_path in overflights:
    try:
        input_raster = Raster(rasters["{overflight}_Total_AudDay"].format(overflight=flight_path))
        output_raster = rasters["Reclass_{overflight}_Total_AudDay"].format(overflight=flight_path)

        # Perform reclassification
        out_raster = Reclassify(input_raster, "VALUE", reclass_rules, "NODATA")
        out_raster.save(output_raster)

        print(f" Reclassified raster saved for {flight_path} - {output_raster}")

    except Exception as e:
        print(f"Error processing AudDay reclassification for {flight_path}: {str(e)}")

print("Reclassification of Total AudDay rasters completed.")

print ("End of part 2 of 3 raster processing.") 


# ----------------------------- #
# Step 6.Raster layer processing part 3 of 3 #
# ----------------------------- #
print("Overflight raster generation part 3 of 3 started.")
# Create TWWHA baseline (OSIvalue5) OSI raster layer

print("Converting TWWHA polygon to raster (Note: Saved in workspace geodatabase directly).")
# Convert TWWHA polygon to raster (Saved in geodatabase directly)
arcpy.conversion.PolygonToRaster(
    layers["TWWHA"], "HECTARES", rasters["TWWHA_polygon_to_raster"], 
    "CELL_CENTER", "NONE", 50
)

# Check if raster was successfully created
if not arcpy.Exists(rasters["TWWHA_polygon_to_raster"]):
    raise ValueError("Error: "+rasters["TWWHA_polygon_to_raster"]+ " does not exist. Check if PolygonToRaster completed successfully.")

# Assign all cells a value of 5 using Con()
constant_raster = Con(Raster(rasters["TWWHA_polygon_to_raster"]) >= 0, 5)

# Save the output as OSI_TWWHA
constant_raster.save(rasters["OSI_TWWHA"])

# Verify if OSI_TWWHA raster contains valid data
osi_min_val = arcpy.GetRasterProperties_management(rasters["OSI_TWWHA"], "MINIMUM").getOutput(0)

if osi_min_val == "NoData":
    raise ValueError("Error: OSI_TWWHA raster contains only NoData values. Something went wrong.")

print("TWWHA OSI raster successfully created with all cells assigned a value of 5.")

# Raster Calculator to combine OSI rasters for each overflight --- this creates the final individual overflight layers #
for overflight in overflights:
    if overflight not in skipped_overflights:
        raster_list = [
            rasters["OSI_TWWHA"],
            rasters["Reclass_{overflight}_HighLow"].format(overflight=overflight),
            rasters["Reclass_{overflight}_PercYr"].format(overflight=overflight),
            rasters["Reclass_{overflight}_Total_AudDay"].format(overflight=overflight),
            rasters["Audible_{overflight}_PolygonToRaster"].format(overflight=overflight)
        ]

        # Ensure all rasters exist before performing calculations
        for raster in raster_list:
            if not arcpy.Exists(raster):
                raise ValueError(f"Missing raster: {raster}, unable to proceed without this dataset.")

        # Sum up OSI layers for the overflight
        output_raster = sum([Raster(r) for r in raster_list])
    
        # Save the output raster
        output_raster.save(rasters["OSI_{overflight}"].format(overflight=overflight))
    else: 
        print(f"Overflight: {overflight} skipped, base datasets were not created.")

print("Individual OSI overflight route scores completed (those skipped listed above, if any). ")

#---- Final Cumulative OSI Layer Creation---#

print("Final cumulative modelling for OSI layer started.")
      
# Define grouped overflight paths
overflight_groups = {
    "Sum_Total_AudDay_SCT": ["PWS_SC_Track_ingress", "PWS_SC_Track_maintenance"],
    "Sum_Total_AudDay_Walls": ["Central_Walls_ingress", "Central_Walls"],
    "Sum_Total_AudDay_Frenchmans": ["Frenchmans_Cap", "Frenchmans_ingress"]
}

# Merge grouped overflight layers using Cell Statistics (SUM)
merged_rasters = {}  # Store intermediate rasters for reuse

for output_name, flight_paths in overflight_groups.items():
    raster_list = [rasters["{overflight}_Total_AudDay"].format(overflight=fp) for fp in flight_paths]

    merged_raster = arcpy.ia.CellStatistics(raster_list, "SUM", "DATA", "SINGLE_BAND")
    merged_raster.save(rasters[output_name])
    
    merged_rasters[output_name] = rasters[output_name]

print("Completed merge step for three paired routes.")

# Merge all overflight rasters using MAXIMUM method
final_merge_list = [
    merged_rasters["Sum_Total_AudDay_SCT"],
    merged_rasters["Sum_Total_AudDay_Frenchmans"],
    merged_rasters["Sum_Total_AudDay_Walls"],
    rasters["{overflight}_Total_AudDay"].format(overflight="Par_Avion_PWS_Melalueca"),
    rasters["{overflight}_Total_AudDay"].format(overflight="Overland_Track"),
    rasters["{overflight}_Total_AudDay"].format(overflight="Maatsuyker")
]

cumulative_raster = arcpy.ia.CellStatistics(final_merge_list, "MAXIMUM", "DATA", "SINGLE_BAND")
cumulative_raster.save(rasters["cumulative_total_AudDay_max"])

# Reclassify the output merged raster using Decision Tree thresholds
reclass_rules = "0 104.190788 0;105 420 -1;NODATA 0"

reclassified_raster = arcpy.sa.Reclassify(
    Raster(rasters["cumulative_total_AudDay_max"]),
    "VALUE",
    reclass_rules,
    "NODATA"
)
reclassified_raster.save(rasters["cumulative_total_AudDay_max_OSI"])

print("Cumulative Total AudDay Max successfully created.")

# Create the final cumulative OSI layer
# Enable overwriting of existing files
arcpy.env.overwriteOutput = True

# List of rasters used in the final cumulative OSI layer
final_rasters = [
    "OSI_TWWHA",
    "cumulative_total_AudDay_max_OSI", 
    "cumulative_days_per_yr",
    "cumulative_highlow_noise",
    "cumulative_audible"
]

# Check if all required rasters exist before processing
for raster in final_rasters:
    if raster not in rasters:
        raise KeyError(f"Missing raster: {raster}")

# Set the processing extent to match the OSI_TWWHA raster
arcpy.env.extent = arcpy.Describe(rasters["OSI_TWWHA"]).extent

# Import CellStatistics from Spatial Analyst
from arcpy.sa import CellStatistics, Raster

# Create list of Raster objects
osi_rasters = [Raster(rasters[r]) for r in final_rasters]

# Perform cell-wise summation, ignoring NoData cells
final_osi_raster = CellStatistics(osi_rasters, statistics_type="SUM", ignore_nodata="DATA")

# Save the cumulative OSI raster
final_osi_raster.save(rasters["OSI"])

print("Cumulative OSI successfully created.")

#Extract by mask using TWWHA layer to complete "OSI_Final"

#Insert Code here for Mask

import arcpy
from arcpy.sa import *

# Ensure Spatial Analyst is available
arcpy.CheckOutExtension("Spatial")

# Set environment settings
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("GDA 1994 MGA Zone 55")
arcpy.env.cellSize = 50

# Define inputs
input_raster = "OSI"  # or a full path if needed
mask_layer = "TWWHA"
output_path = os.path.join(workspace, "OSI_Final")

# Apply the mask
masked_raster = ExtractByMask(input_raster, mask_layer)
masked_raster.save(output_path)

# Create the final cumulative OSI layer
# Enable overwriting of existing files
arcpy.env.overwriteOutput = True


print("OSI_Final layer created successfully.")



#Step 7 (final)
import arcpy
import os

# Project and map
project = arcpy.mp.ArcGISProject("CURRENT")
m = project.listMaps("Map")[0]

# Raster name (already exists in workspace)
raster_name = "OSI_Final"
raster_path = os.path.join(workspace, raster_name)  # use the previously defined workspace

# Check that raster exists
if arcpy.Exists(raster_path):
    print("Raster exists:", raster_path)
else:
    raise ValueError(f"Raster '{raster_name}' does not exist in workspace {workspace}!")

# Add raster to map
m.addDataFromPath(raster_path)
print(f"Raster '{raster_name}' added to map.")



