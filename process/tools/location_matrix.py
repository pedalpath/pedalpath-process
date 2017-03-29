import numpy

class Data:
    def __init__(self,data):
        self.id = data['id']
        for (key,value) in data.items():
            setattr(self,key,value)
    def __hash__(self):
        return hash(self.id)

class LocationMatrix:

    SIZE = 1000
    # 111,111 meters (111.111 km) in the y direction is 1 degree (of latitude)
    # 111,111 * cos(latitude) meters in the x direction is 1 degree (of longitude)

    def __init__(self,Data=Data):
        self.Data = Data
        self.matrix = {}

    def _ref(self,degrees):
        return str(self._round(degrees))

    def _round(self,degrees):
        return int(round(degrees*self.SIZE))

    def insert(self,lat,lon,data):
        lat_ref = self._ref(lat)
        lon_ref = self._ref(lon)
        self.matrix[lat_ref] = self.matrix.get(lat_ref,{})
        self.matrix[lat_ref][lon_ref] = self.matrix[lat_ref].get(lon_ref,[])
        self.matrix[lat_ref][lon_ref].append(data)

    def get(self,lat,lon):
        lat_ref = self._ref(lat)
        lon_ref = self._ref(lon)
        row = self.matrix.get(lat_ref,{})
        return row.get(lon_ref,[])
        
    def find(self,lat,lon):
        cell = self.get(lat,lon)
        if (len(cell)): return cell
        for i in range(-1,2,2):
            for j in range(-1,2,2):
                _lat = lat+(i*self.SIZE)
                _lon = lon+(j*self.SIZE)
                cell = self.get(_lat,_lon)
                if (len(cell)): return cell

    def segment(self,coordinate_a,coordinate_b):
        "find all the points in the line between a and b"

        (lat_a,lon_a) = coordinate_a
        (lat_b,lon_b) = coordinate_b

        # Full range of lats and lons
        lat_range = abs(lat_a-lat_b)
        lon_range = abs(lon_a-lon_b)

        # The number of samples based on size of quare
        number = max(2,int(100 * max(lat_range,lon_range) * self.SIZE))

        # Sample the line at intervals
        lats = numpy.linspace(lat_a,lat_b,number)
        lons = numpy.linspace(lon_a,lon_b,number)

        # Collect all cells on the way
        collection = set()
        for (lat,lon) in zip(lats,lons):
            cell = self.get(lat,lon)
            collection = collection | set(cell)

        return collection

    def path(self,coordinates):
        "query a list of coordinates"

        collection = set()
        for i in range(1,len(coordinates)):
            collection = collection | self.segment(coordinates[-1],coordinates[0])

        return list(collection)

    def to_json(self):
        return self.matrix

    def from_json(self,matrix):
        self.matrix = {
            lat: {
                lon: [
                    self.Data(data)
                    for data in cell
                ]
                for lon, cell in row.items()
            }
            for lat,row in matrix.items()
        }

if (__name__ == "__main__"):

    matrix = LocationMatrix()
    matrix.insert(51.4684607,-0.0915444,'node1')
    matrix.insert(51.4434222,-0.0892823,'node2')
    matrix.insert(51.4434362,-0.0893527,'node3')
    print(matrix.matrix)
    print(matrix.get(51.4684607,-0.0915444))
    print(matrix.get(51.4434222,-0.0892823))
    print(matrix.get(51.4434362,-0.0893527))

    print(matrix.segment((51.4434222,-0.0892823),(51.4434362,-0.0893527)))

