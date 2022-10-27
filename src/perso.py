# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 14:50:56 2022

@author: LDE
"""

PROGRAM Main
// Version 0.1 Test_vision_DEVL
VAR
	iCamera : 						INT 	:= 0;				// Step du séquenceur

	//timer imgs
	tWaitFirstImg	: 	TON				;
	bWaitFirstImg	:	BOOL			;
	
	tWaitSecondImg	:	TON				;
	bWaitSecondImg	:	BOOL 			;
	
	tResetGrabImg 	:	TON				;
	bResetGrabImg	: 	BOOL			;
	
	tWaitPrint		:	TON				;
	bWaitPrint		: 	BOOL:=FALSE			;
	tResetPrint		:	TON				;
	bResetPrint		: 	BOOL			;
	
	bSimuOn			: BOOL				;
	

	
	// Interface Capsuleuse
	bCapsCheckLot1 		AT%I* : 	BOOL;
	bCapsCheckLot2 		AT%I* : 	BOOL;
	bCapsVisionReady 	AT%Q* : 	BOOL;
	bCapsLotOK 			AT%Q* : 	BOOL;
	bCapsDataValid 		AT%Q* : 	BOOL;
	bFirstSecond 		AT%Q* : 	BOOL;
	
	bPrinterStart	: BOOL;

	// Interface caméra/Eclairage
	bLightOn 			AT%Q* : 	BOOL;
	bGrabImage 			AT%Q* : 	BOOL;

	// Timers	
	
	tFirstImageDelay : 				TIME 	:= T#190MS;
	tSecondImageDelay : 			TIME 	:= T#70MS;
	tLightPreDelay : 				TIME 	:= T#10MS;
	tLightPostDelay : 				TIME 	:= T#10MS;
	
	// Divers
	bWaitFirstImage : 				BOOL;
	bWaitSecondImage : 				BOOL;
	// Simulation de la capsuleuse	
	tCycle : 						TON;

END_VAR



tWaitFirstImg(IN := bWaitFirstImg, PT := T#320MS);
tWaitSecondImg(IN := bWaitSecondImg, PT := T#70MS);
tResetGrabImg(IN := bResetGrabImg, PT := T#1MS);

tWaitPrint(IN := bWaitPrint, PT := T#700MS);
tResetPrint(IN := bResetPrint, PT := T#1MS);

bPrinterStart :=FALSE;
BSimuOn := FALSE;
bLightOn := TRUE;

// Transfert vers la capsuleuse




IF bCapsCheckLot2 THEN
	bWaitPrint := TRUE;
END_IF

IF tResetPrint.Q THEN
	bResetPrint := FALSE;
	bPrinterStart := FALSE;
	IF bSimuOn THEN
		bWaitPrint := TRUE;
	END_IF
		
END_IF


IF tWaitPrint.Q THEN
	bPrinterStart := TRUE;
	bWaitPrint := FALSE;
	bResetPrint := TRUE;
END_IF
	

IF tResetGrabImg.Q THEN
	bGrabImage := FALSE;
	bResetGrabImg := FALSE;
END_IF

CASE iCamera OF
	0:
		//IF the printer starts the timer 
		IF bPrinterStart THEN
			bWaitFirstImg := TRUE;
			iCamera := 10;
			bFirstSecond := TRUE;
		END_IF
	10:
		//when the timer give the signal
		//active the second timer, reset the first
		//get an image 
		IF tWaitFirstImg.Q THEN
			bWaitFirstImg := FALSE;
			bWaitSecondImg := TRUE;
			bGrabImage := TRUE;
			bResetGrabImg := TRUE;
			
			iCamera := 20;

		END_IF
	20:
		IF tWaitSecondImg.Q THEN
			bWaitSecondImg := FALSE;
			bGrabImage := TRUE;
			bResetGrabImg := TRUE;
			iCamera := 0;
			bFirstSecond := FALSE;
			
		END_IF
END_CASE


