import { Component, Input, OnInit } from '@angular/core';
import {MatSnackBar} from '@angular/material/snack-bar';
import { Router } from '@angular/router';
// import { ModalsModule, WidgetsModule } from '../../../../../../partials';


@Component({
  selector: 'app-custom-table',
  templateUrl: './custom-table.component.html',
  styleUrls: ['./custom-table.component.scss'],
  // imports: [MatSnackBar]
})
export class CustomTableComponent implements OnInit {
  @Input() tableOuterTitle: string = "Recent Posts";
  @Input() sortingOpt: boolean = false;
  @Input() postSaved: boolean = false;
ShowModal : boolean = false;
openModal() {
  this.ShowModal = true;
}
closeModal() {
  this.ShowModal = false;
}
// This is the flag icons library we are using, you can see the countries short names here
// https://flagicons.lipis.dev/

items: Array<{ title: string; company?: string; companyLogo?: string; flagClass?: string; country?: string; city?: string; program?: string; programType?: string; deadline?: string; jobLink?: string }>;
  constructor(private _snackBar: MatSnackBar, private router : Router) {}
  
  ngOnInit(): void {
    this.items = [
      { title: "Risk Data Analyst support", company: "BNP Paribas", companyLogo: "./assets/media/company/bnp_paribas.svg", flagClass: "fi fi-it", country: "Italy", city: "Milan", program: "Internship", programType: "internship", deadline: "", jobLink: "https://group.bnpparibas/en/careers/job-offer/risk-data-analyst-support" },
      { title: "Beca ADE o Economía Política Riesgo BNP Paribas Personal Finance", company: "BNP Paribas", companyLogo: "./assets/media/company/bnp_paribas.svg", flagClass: "fi fi-id", country: "Indonesia", city: "Jakarta", program: "Internship", programType: "internship", deadline: "", jobLink: "https://group.bnpparibas/en/careers/job-offer/beca-ade-o-economia-politica-riesgo-bnp-paribas-personal-finance-1" },
      { title: "Stage Analyste Junior M&A (H/F) - janvier 2024", company: "Lazard", companyLogo: "./assets/media/company/lazard.svg", flagClass: "fi fi-fr", country: "France", city: "Paris", program: "Internship", programType: "internship", deadline: "", jobLink: "https://lazard-careers.tal.net/vx/lang-en-GB/mobile-0/appcentre-1/brand-4/xf-4045e3fdcf1d/candidate/so/pm/1/pl/2/opp/999-Stage-Analyste-Junior-M-A-H-F-janvier-2024/en-GB" },
      { title: "STAGIAIRE PERFECTIONNEMENT BAC +2/3", company: "BNP Paribas", companyLogo: "./assets/media/company/bnp_paribas.svg", flagClass: "fi fi-ci", country: "Ivory Coast", city: "Abidjan Autonomous District", program: "Internship", programType: "internship", deadline: "", jobLink: "https://group.bnpparibas/en/careers/job-offer/stagiaire-perfectionnement-bac-2-3" },
      { title: "Trainee - Business Revenue Officer (M/F)", company: "BNP Paribas", companyLogo: "./assets/media/company/bnp_paribas.svg", flagClass: "fi fi-lu", country: "Luxembourg", city: "Luxembourg", program: "Internship", programType: "internship", deadline: "", jobLink: "https://group.bnpparibas/en/careers/job-offer/trainee-business-revenue-officer-m-f" },
      { title: "STAGIAIRE H/F – PRIVATE EQUITY", company: "Lazard", companyLogo: "./assets/media/company/lazard.svg", flagClass: "fi fi-fr", country: "France", city: "Paris", program: "Full Time", programType: "fulltime", deadline: "", jobLink: "https://lazard-careers.tal.net/vx/lang-en-GB/mobile-0/appcentre-1/brand-4/xf-4045e3fdcf1d/candidate/so/pm/1/pl/2/opp/699-STAGIAIRE-H-F-PRIVATE-EQUITY/en-GB" },
      { title: "STAGE - ASSET VALUATION SUPPORT", company: "BNP Paribas", companyLogo: "./assets/media/company/bnp_paribas.svg", flagClass: "fi fi-it", country: "Italy", city: "Florence", program: "Internship", programType: "internship", deadline: "", jobLink: "https://group.bnpparibas/en/careers/job-offer/stage-asset-valuation-support-1" },
      { title: "2023 Brazil Global Transaction Services Internship Program", company: "Bank of America", companyLogo: "./assets/media/company/bank_of_america.svg", flagClass: "fi fi-br", country: "Brazil", city: "Sao Paulo", program: "Internship", programType: "internship", deadline: "", jobLink: "https://bankcampuscareers.tal.net/vx/lang-en-GB/mobile-0/brand-4/xf-3401d91cd29a/candidate/so/pm/1/pl/1/opp/9637-2023-Brazil-Global-Transaction-Services-Internship-Program/en-GB" },
      { title: "Beca ADE/MARKETING Marketing Retail BNP Paribas Personal Finance", company: "BNP Paribas", companyLogo: "./assets/media/company/bnp_paribas.svg", flagClass: "fi fi-es", country: "Spain", city: "Madrid", program: "Internship", programType: "internship", deadline: "", jobLink: "https://group.bnpparibas/en/careers/job-offer/beca-ade-marketing-beca-transformacion-digital-y-proyectos-bnp-paribas-personal-finance-2" },
      { title: "2024 Investment Management Summer Analyst Program - Private Markets Solutions (West Conshohocken)", company: "Morgan Stanley", companyLogo: "./assets/media/company/morgan_stanley.svg", flagClass: "fi fi-us", country: "US", city: "West Conshohocken", program: "Internship", programType: "internship", deadline: "Jul 14, 2023", jobLink: "https://www.morganstanley.com/careers/students-graduates/opportunities/14823" },
      { title: "Stage – Analyste Développement Durable – Merchant Banking – Septembre 2023", company: "RothsChild", companyLogo: "./assets/media/company/rothschild.svg", flagClass: "", country: "", city: "", program: "Long Term Internship", programType: "ltintern", deadline: "31 Aug 2023", jobLink: "https://rothschildandco.tal.net/vx/lang-en-GB/mobile-0/appcentre-1/brand-4/xf-b3f50d346ea3/candidate/so/pm/1/pl/2/opp/424-Stage-Analyste-D%C3%A9veloppement-Durable-Merchant-Banking-Septembre-2023/en-GB" },
    ]
  }
  openSnackBar(message: string) {
    this._snackBar.open(message, '', {
      duration: 3000,
      verticalPosition: "bottom",
      horizontalPosition: "center"
    });
    this.postSaved = true;
  }
  goToPage(pageName:string){
    this.router.navigate([`${pageName}`]);
  }
}
