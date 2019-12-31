import { Component} from '@angular/core';
import { FencerService } from './fencer.service';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  constructor(private fencerService:FencerService) {  }
  someProperty:string = '';

  ngOnInit() {
    
    
    console.log(this.fencerService.cars);

    this.someProperty = this.fencerService.myData();
  }
}
