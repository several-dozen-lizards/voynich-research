import json, hashlib, html
from pathlib import Path
P=Path(__file__).resolve().parent
panels=[]
def panel(folio,sign,oid,region,display,groups,note=''):
    # rows: head x,y; adjacent label anchor x,y (0,0 = unresolved);
    # torso B=bare G=garment ?=ambiguous; enclosure V=visible N=absent ?=ambiguous.
    rows=[]
    for group,text in groups.items():
        for i,line in enumerate(text.strip().splitlines(),1):
            x,y,lx,ly,b,v=line.split(); x,y,lx,ly=map(float,(x,y,lx,ly))
            def transform(a,b):return [round(region[0]+(a-display[0])*region[2]/display[2]),round(region[1]+(b-display[1])*region[3]/display[3])]
            rows.append(dict(id=f'{folio}-{group}-{i:02}',group=group,index=i,head=transform(x,y),label_anchor=transform(lx,ly) if lx else None,body={'B':'bare torso visible','G':'garment visible','?':None}[b],enclosure={'V':'enclosing vessel visible','N':'no enclosing vessel visible','?':None}[v],star_pigmentation=None,star_reason='Pale strokes versus pigment cannot be classified reliably at reviewed display resolution.',label_association='adjacent candidate; no explicit figure-to-text leader established' if lx else 'unresolved: no unique adjacent label assigned',ambiguity=('Torso unclear. ' if b=='?' else '')+('Enclosure unclear. ' if v=='?' else ''),review='visual first pass; coordinates approximate, not precision boundaries'))
    panels.append(dict(folio=folio,sign=sign,oid=oid,region=region,rows=rows,note=note))
panel('f70v1','Aries','1006201',[300,450,2600,2400],[250,0,780,720],{
'outer':'''670 70 750 110 B V
860 150 905 240 B V
960 320 942 402 B V
940 485 890 540 B V
865 590 810 622 B V
710 665 625 645 B V
545 635 480 580 B V
420 535 395 440 B V
365 375 395 290 B V
450 160 520 140 B V''',
'inner':'''660 200 735 240 B V
815 320 810 390 B V
740 515 655 515 B V
525 455 520 345 B V
540 250 605 245 B V'''})

panel('f71r','Aries','1006202',[100,450,2400,2600],[308,0,664,720],{
'outer':'''630 70 715 100 G V
780 110 838 175 G V
900 230 900 325 G V
930 390 890 470 ? V
835 575 750 610 G V
670 650 580 630 G V
480 620 405 540 G V
365 430 365 350 G V
365 265 420 190 G V
475 120 560 105 G V''',
'inner':'''700 215 760 295 G V
810 395 755 475 G V
665 520 580 515 ? V
480 450 477 340 ? V
520 230 620 210 G V'''},'An isolated hatched form near upper-left margin is retained as a non-figure mark, not an extra nymph.')

panel('f71v','Taurus','1006203',[200,350,2250,2250],[280,0,720,720],{
'outer':'''680 80 753 110 G V
825 130 869 196 G V
923 248 910 325 G V
940 377 910 460 G V
850 545 780 576 ? V
705 600 600 580 ? V
515 550 465 472 ? V
426 400 430 320 G V
433 230 490 170 G V
544 110 620 100 G V''',
'inner':'''680 183 756 228 G V
815 320 810 385 ? V
710 500 645 480 ? V
526 400 541 330 ? V
548 264 616 225 G V'''})

panel('f72r1','Taurus','1006203',[2300,100,2100,2750],[365,0,550,720],{
'outer':'''585 133 640 148 B N
704 147 742 185 B N
780 213 796 265 B N
823 307 811 358 B N
810 420 772 463 B N
708 535 620 540 B N
505 532 472 483 B N
410 405 438 343 B N
414 292 455 253 B N
456 182 522 153 B N''',
'inner':'''602 216 675 247 B V
709 272 711 358 B V
699 427 623 451 B V
555 448 521 405 B V
494 364 538 253 ? ?'''},'Inner left figure is next to a physical hole. Torso/enclosure ambiguity retained; adjacent label anchor is especially uncertain.')

panel('f70v2','Pisces','1006200',[650,300,2650,2850],[306,0,669,720],{
'outer':'''650 47 670 126 B V
710 70 743 142 B V
790 90 803 181 B V
860 140 856 229 B V
910 210 899 278 B V
950 310 935 376 B V
950 430 916 483 B V
900 530 842 556 B V
820 605 761 617 B V
720 655 661 640 B V
590 650 543 637 B V
485 620 447 559 B V
405 520 390 475 B V
365 435 350 367 B V
365 310 393 265 B V
410 200 449 199 ? V
455 130 494 163 ? V
525 80 546 142 B V
590 50 608 124 B V''',
'inner':'''655 160 708 170 B V
770 215 815 244 B V
845 310 846 376 B V
820 455 789 500 B V
735 540 672 566 B V
615 570 565 550 B V
500 480 517 535 ? V
460 360 454 424 B V
480 260 457 321 ? V
565 175 613 180 B V'''},'29 peripheral figures located, not30. Fold obscures some left-side details. Excluded from primary 30-degree alignment by frozen rule; no inserted gap.')

panel('f72r2','Gemini','1006203',[3950,0,2450,2850],[331,0,618,720],{
'extra-top':'''435 140 478 120 B N
515 85 563 105 B N
610 65 642 102 B N
680 70 709 107 B N
770 90 796 136 B N''',
'outer':'''600 150 637 168 B N
670 153 702 171 B N
743 186 772 232 B N
803 250 786 298 B N
830 350 806 397 B N
807 464 763 484 B N
730 542 678 543 B N
621 568 623 589 B N
547 554 515 560 ? N
493 510 480 543 B N
452 466 480 474 ? N
435 413 455 441 ? N
435 356 0 0 ? N
442 300 456 337 B N
455 246 479 252 B N
522 180 565 196 B N''',
'inner':'''610 245 634 260 B N
667 246 686 273 B N
724 290 715 329 B N
744 376 713 417 B N
684 465 648 447 B N
607 475 583 462 B N
552 449 558 409 B N
515 370 548 343 B N
550 275 578 283 B N'''},'Count from images: 5 extra-top,16 outer,9 inner. Lower and left close-ups checked. One left-side label association unresolved; lower-right outer star attachment not established. Extra group is not assigned a degree position.')

panel('f72r3','Cancer','1006203',[0,0,1400,1021],[0,0,1400,1021],{
'outer':'''780 130 833 169 B N
918 160 956 225 B N
1025 250 1055 329 ? ?
1110 380 1110 475 B N
1070 630 1030 714 B N
945 815 857 817 B N
735 850 669 798 B N
590 785 541 725 B N
470 675 0 0 ? N
470 350 514 435 ? N
540 230 602 204 B N
655 150 732 168 B N''',
'middle':'''775 235 826 260 B N
888 255 924 307 B N
965 335 991 380 ? ?
1005 420 1040 475 ? ?
1025 550 990 622 ? ?
920 710 827 735 B N
705 730 654 716 B N
570 625 580 570 B N
530 510 565 448 ? N
552 350 610 332 B N
658 260 721 270 B N''',
'inner':'''770 340 817 383 B N
885 390 888 467 B N
930 525 885 586 B N
790 650 721 626 B N
670 600 627 551 B N
625 490 637 431 B N
670 375 730 394 B N'''},'Reviewed from saved v31 expanded source image as well as Yale overview. Coordinate space is the local 1400x1021 crop, not original Yale pixels. Three bands:12/11/7; no equal-band assumption. Fold obscures several right-side details.')
panels[-1]['coordinate_space']='local:f72r3-expanded.jpg'
panels[-1]['local_image']='f72r3-expanded.jpg'

panel('f72v3','Leo','1006204',[700,250,2900,3100],[0,0,1526,1632],{
'outer':'''850 150 890 240 B N
1000 190 1050 290 B N
1200 275 1210 370 B N
1340 400 1330 530 B N
1440 600 1410 670 B N
1440 755 1410 840 B N
1410 910 1390 1000 B N
1340 1160 1300 1250 B N
1060 1380 1100 1410 B N
800 1450 710 1390 B N
520 1350 490 1410 B N
350 1130 320 1220 ? N
250 940 280 1010 B N
230 770 300 690 B N
280 580 350 530 B N
410 380 440 410 ? ?
520 235 600 300 B N
695 165 740 230 B N''',
'inner':'''755 400 830 480 B N
950 390 1010 510 B N
1090 490 1120 580 B N
1200 630 1170 720 B N
1240 800 1190 880 B N
1180 1010 1110 1080 B N
1000 1170 940 1220 B N
750 1220 670 1150 B N
530 1050 570 1110 ? N
480 900 610 900 ? ?
480 700 560 680 ? ?
600 480 690 530 B N'''},'Wider local Yale crop checked to retain circle extent. One upper-left fold location is a possible obscured figure, not a confirmed thirtieth figure. Inventory is29 clear/candidate heads plus1 uncertain-presence location; no degree alignment permitted until resolved.')
panels[-1]['local_image']='leo-wide.jpg'
for r in panels[-1]['rows']:
 if r['id']=='f72v3-outer-16':
  r['presence']='uncertain: fold obscures head/body identification'
  r['ambiguity']+=' Possible figure location at fold; do not count as confirmed.'

def output():
 (P/'ANNOTATIONS.json').write_text(json.dumps(panels,indent=2),encoding='utf-8')
 print([(p['folio'],len(p['rows'])) for p in panels])
if __name__=='__main__':output()
