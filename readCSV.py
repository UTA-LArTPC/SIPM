import csv
import sys, os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import ROOT
import sip
from collections import defaultdict
import numpy
from array import array
import matplotlib.pyplot as plt

from ROOT import TCanvas, TPad, TFormula, TF1, TPaveLabel, TH1F, TFile
from ROOT import gROOT, gBenchmark, Double, gSystem

columns = defaultdict(list) # each value in each column is appended to a list

c1 = TCanvas('c1', 'Dynamic Filling Example', 200, 10, 700, 500)


# For speed, bind and cache the Fill member functions,
histos = ['h1f']


varx = Double()
vary = Double()
files = os.listdir(os.getcwd())

channels = []
channel_files = []

for File in files:
    if File[-4:] == ".csv":
	chIndex = File.lower().find("ch")
	areaIndex = File.lower().find("area")
	if (File[chIndex:areaIndex] not in channels):
		channels.append(File[chIndex:areaIndex])

for channel in channels:
	with open(channel + "_data.txt", "w") as ch:
		channel_files.append(channel + "_data.txt")

for File in files:
    if File[-4:] == ".csv":
    	with open(File) as f:
		h1f = TH1F( File[:-4] , 'Test ', 2000, -10, 10 )
		#h1f = TH1F( 'h1f' , 'Test ', 300, -3, 3 )
		# For speed, bind and cache the Fill member functions,
		histos = [ 'h1f' ]
		for name in histos:
    			exec('%sFill = %s.Fill' % (name,name))
    		reader = csv.reader(f)
    		reader.next()
    		for row in reader:
    		    for (i,v) in enumerate(row):
            		if i == 0:
				varx =  float(v)
			    	varx = varx * 10**6
			    	
			if i == 1:
			    	vary = float(v)
			    	vary = vary 
			    	h1f.Fill(varx, vary)
                		columns[i].append(v)

    	par = array('d', 3*[0.])
    	g1 = TF1('g1', 'gaus',  -10, 10)
	g1.SetLineColor(2)
    	h1f.Fit(g1, 'R+')
    	par1 = g1.GetParameters()
	norm = str(par1[0])
	mean = str(par1[1])
	rms = str(par1[2])
        print(File[-24:-23], File[-22:-21], par1[0], par1[1], par1[2])
	for ch_data_f in channels:
		if ch_data_f.lower() in File.lower():
			with open(ch_data_f + "_data.txt", "a") as channel_data:
				channel_data.write(File[-24:-23])
				channel_data.write(".")
				channel_data.write(File[-22:-21])
				channel_data.write(",")
				channel_data.write(norm)
				channel_data.write(",")
				channel_data.write(mean)
				channel_data.write(",")
				channel_data.write(rms)
				channel_data.write("\n")
			

    	myfile = TFile( File[:-4]+'.root', 'RECREATE')
    	#h1f.Write()
	#h1f.Draw("histo")
    	myfile.Close()	

def showPE(data_files, combine=False):
	x_intensity = {}
	y_PE = {}

	for i in range(0, len(data_files)):
		x_intensity["ch" + str(i + 1)] = []
		y_PE["ch" + str(i + 1)] = []

	for data in data_files:
		data = open(data, "r")
		for line in data.read().split("\n")[:-1]:
			intensity = float(line.split(",")[0])
			norm = float(line.split(",")[1])
			mean = float(line.split(",")[2])
			rms = float(line.split(",")[3])
			numPE = (mean**2)/(rms**2)
			for ch_data_f in channels:
				if ch_data_f.lower() in data.name.lower():
					x_intensity[ch_data_f.lower()].append(intensity)
					y_PE[ch_data_f.lower()].append(numPE)
	plt.xlabel("LED Intensity (%)")
	plt.ylabel("Number of photoelectrons")
	if combine==True:
		plt.title("Number of Photoelectrons vs LED Intensity")
		plt.legend(loc='upper left')
		for i in range(0, len(data_files)):
			plt.scatter(x_intensity["ch" + str(i + 1)], y_PE["ch" + str(i + 1)], label="Channel " + str(i + 1))
		plt.legend()
		plt.show()
	else:
		for i in range(0, len(data_files)):
			plt.title("Number of Photoelectrons vs LED Intensity [Channel " + str(i + 1) + "]")
			plt.scatter(x_intensity["ch" + str(i + 1)], y_PE["ch" + str(i + 1)])
			plt.show()		
	for data in data_files:
		data = open(data, "r")
		data.close()

viewSep = raw_input("Would you like to view each channel separately? (y/n) ").lower()
if "y" in viewSep:
	showPE(channel_files, False)
else:
	showPE(channel_files, True)

files = os.listdir(os.getcwd())
for File in files:
    if File[-3:] != ".py" and File[-4:] != ".txt" and File[-4:] != ".git":
	os.remove(File)
