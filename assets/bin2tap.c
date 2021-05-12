/*
 *	Quick 'n' dirty mym to tap converter
 *
 *	Usage: bin2tap [binfile] [tapfile]
 *         or: bin2tap [binfile] [tapfile] [start]
 *         or: bin2tap [binfile] [tapfile] [start] [execution]
 *
 *	zack 8/2/2000
 *	Modified by Stefano	3/12/2000
 *      Modified by Metalbrain 27/06/2002
 *
 *	Creates a new TAP file (overwriting if necessary) just ready to run.
 */

#include <stdio.h>

/* Stefano reckons stdlib.h is needed for binary files for Win compilers*/
#include <stdlib.h>

unsigned char parity;

void writebyte(unsigned char, FILE *);
void writenumber(unsigned int, FILE *);
void writeword(unsigned int, FILE *);

int main(int argc, char *argv[])
{
	char	name[11];
	FILE	*fpin, *fpout;
	int	c;
	int	i;
	int	len;
        int     datastart;
        int     exeat;

        if ( (argc<3) || (argc>5) ) {
		fprintf(stdout,"Usage: %s [code file] [tap file]\n",argv[0]);
                fprintf(stdout,"   or: %s [code file] [tap file] [start]\n",argv[0]);
                fprintf(stdout,"   or: %s [code file] [tap file] [start] [execution]\n",argv[0]);
		exit(1);
	}

        if (argc==3)
                {
                datastart=32768;
                exeat=32768;
                }
        else
                {
                datastart=atoi(argv[3]);
                if ((datastart<0)||(datastart>65536))
                        {
                        fprintf(stdout,"Invalid start address: B Integer Out of Range");
                        exit(1);
                        }
                if (argc==4)
                        {
                        exeat=datastart;
                        }
                else
                        {
                        exeat=atoi(argv[4]);
                        if ((exeat<0)||(exeat>65536))
                                {
                                fprintf(stdout,"Invalid execution address: B Integer Out of Range");
                                exit(1);
                                }
                        }
                }

	if ( (fpin=fopen(argv[1],"rb") ) == NULL ) {
                fprintf(stdout,"Can't open input file\n");
		exit(1);
	}


/*
 *	Now we try to determine the size of the file
 *	to be converted
 */
	if	(fseek(fpin,0,SEEK_END)) {
		printf("Couldn't determine size of file\n");
		fclose(fpin);
		exit(1);
	}

	len=ftell(fpin);

	fseek(fpin,0L,SEEK_SET);

	if ( (fpout=fopen(argv[2],"wb") ) == NULL ) {
		printf("Can't open output file\n");
		exit(1);
	}

/* Write a BASIC loader, first */

        fputc(0x13,fpout);
        fputc(0,fpout);
        fputc(0,fpout);
        parity=0x31;            // initial checksum
        writebyte(0,fpout);

        fprintf(fpout,"loader    ");
        writebyte(0x1e,fpout);      /* line length */
        writebyte(0,fpout);
        writebyte(0x0a,fpout);      /* 10 */
        writebyte(0,fpout);
        writebyte(0x1e,fpout);      /* line length */
        writebyte(0,fpout);
        writebyte(0x1b,fpout);
        writebyte(0x20,fpout);
        writebyte(0,fpout);
        writebyte(0xff,fpout);
        writebyte(0,fpout);
        writebyte(0x0a,fpout);
        writebyte(0x1a,fpout);
        writebyte(0,fpout);
        writebyte(0xfd,fpout);      /* CLEAR */
        writebyte(0xb0,fpout);      /* VAL */
        writebyte('\"',fpout);
        writenumber(datastart-1,fpout);
        writebyte('\"',fpout);
        writebyte(':',fpout);
        writebyte(0xef,fpout);      /* LOAD */
        writebyte('\"',fpout);
        writebyte('\"',fpout);
        writebyte(0xaf,fpout);      /* CODE */
        writebyte(':',fpout);
        writebyte(0xf9,fpout);      /* RANDOMIZE */
        writebyte(0xc0,fpout);      /* USR */
        writebyte(0xb0,fpout);      /* VAL */
        writebyte('\"',fpout);
        writenumber(exeat,fpout);
        writebyte('\"',fpout);
        writebyte(0x0d,fpout);
        writebyte(parity,fpout);

/* Write out the code header file */
	fputc(19,fpout);	/* Header len */
	fputc(0,fpout);		/* MSB of len */
	fputc(0,fpout);		/* Header is 0 */
	parity=0;
	writebyte(3,fpout);	/* Filetype (Code) */
/* Deal with the filename */
	if (strlen(argv[1]) >= 10 ) {
		strncpy(name,argv[1],10);
	} else {
		strcpy(name,argv[1]);
		strncat(name,"          ",10-strlen(argv[1]));
	}
	for	(i=0;i<=9;i++)
		writebyte(name[i],fpout);
	writeword(len,fpout);
        writeword(datastart,fpout); /* load address */
	writeword(0,fpout);	/* offset */
	writebyte(parity,fpout);
/* Now onto the data bit */
	writeword(len+2,fpout);	/* Length of next block */
	parity=0;
	writebyte(255,fpout);	/* Data... */
	for (i=0; i<len;i++) {
		c=getc(fpin);
		writebyte(c,fpout);
	}
	writebyte(parity,fpout);
	fclose(fpin);
	fclose(fpout);
}

void writenumber(unsigned int i, FILE *fp)
{
        int c;
        c=i/10000;
        i-=c*10000;
        writebyte(c+48,fp);
        c=i/1000;
        i-=c*1000;
        writebyte(c+48,fp);
        c=i/100;
        i-=c*100;
        writebyte(c+48,fp);
        c=i/10;
        writebyte(c+48,fp);
        i%=10;
        writebyte(i+48,fp);
}



void writeword(unsigned int i, FILE *fp)
{
	writebyte(i%256,fp);
	writebyte(i/256,fp);
}



void writebyte(unsigned char c, FILE *fp)
{
	fputc(c,fp);
	parity^=c;
}
