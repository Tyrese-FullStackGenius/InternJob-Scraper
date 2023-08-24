import { Pipe, PipeTransform } from '@angular/core'

@Pipe({
  name: 'pluck',
})
export class PluckPipe implements PipeTransform {
  transform(input: any[], key: string): any {
    const arr = input.map(value => value[key])
    return [...new Set(arr)].filter(v => v !== null)
  }
}
