import ast, datetime, pickle
from zeep import Client

class LottoInOut(object):
    def __init__(self):
        self.resultsDb = self.load_cache()

    def load_cache(self):
        try:
            with open('outfile.cache', 'rb') as fp:
                loadList = pickle.load(fp)
            print("Cache loaded from a disk...")
            return loadList
        except:
            self.save_cache([])
            return []


    def save_cache(self, list):
        with open('outfile.cache', 'wb') as fp:
            pickle.dump(list, fp)
        return True

    def fetch_drawn_data(self, date):
        """SOAP data parsing
        :arg date
        :return zwraca najblizszy dzien losowania ponad data"""
        soap_url = 'http://serwis.mobilotto.pl/mapi/index.php?soap=ssv1.wsdl'
        print('Fetching data from LOTTO SOAP...')
        client = Client(soap_url)
        result = str(client.service.getLastWyniki(date))
        result_dict = ast.literal_eval(result)
        try:
            results = (result_dict['wynikiLotto']['WynikLotto'])[0]
            return results
        except:
            print('Error! No data fetched!')
            return False

    def get_resultsDb(self):
        for line in self.resultsDb:
            print line

    def get_cache(self):
        for line in self.load_cache():
            print line

class Lotto(LottoInOut):
    """Function and methods to work on Lotto data
    :arg date of release
    """
    last_url = 'http://app.lotto.pl/wyniki/?type=dl'
    archive_url = 'http://serwis.mobilotto.pl/mapi/index.php?soap=ssv1.wsdl'

    def __init__(self):
        super(Lotto, self).__init__()
        self.drawnData = None
        self.drawnNumbers = None
        self.date = None
        self.hits = []
        self.handNumbers = []

    def get_results(self):
        """
        Getter for main class data variables
        :return: results list, datetime format date
        """
        return self.drawnNumbers, self.date

    def check_numbers(self, handNumbers, date):
        # TODO Weryfikacja daty losownia oraz jej korekta (najblizsze losowanie)
        # Check if it is in the cache
        self.drawnData = self.find_in_list(self.resultsDb, date)
        if not self.drawnData:
            # If data not in the cache download data from Lotto API
            fetchedData = self.fetch_drawn_data(date)
            if fetchedData:
                if self.append_to_list(fetchedData) != False:
                    self.save_cache(self.resultsDb)  # Save new DB to cache disk
                    self.drawnData = fetchedData
                else:
                    return False
            else:
                return False
        # Mapping data to class variables
        self.date = self.drawnData['data_losowania'][:10]
        self.drawnNumbers = map(int, self.drawnData['numerki'].split(','))
        self.handNumbers = handNumbers
        self.hits = [num for num in handNumbers if num in self.drawnNumbers]
        return self.hits

    def append_to_list(self, drawnData):
        if not self.find_in_list(self.resultsDb, drawnData['data_losowania'][:10]):
            self.resultsDb.append(drawnData)
        else:
            return False

    def find_in_list(self, drawnNumbers, date):
         try:
            for number in drawnNumbers:
                if number['data_losowania'][:10] == date: return number
            return False
         except:
             return False

    def drawResult(self, results, hits):
        if not hits:
            return results
        newResult = ''
        for letter in results:
            if letter in hits:
                newResult += '<b>(' + str(letter) + ')</b>, '
                continue
            newResult += str(letter) + ', '
        return newResult[:-2]

    def __str__(self):
        if self.drawnNumbers:
            retString = 'Kupon: %s. Losowanie: %s. Trafiles %i: %s' % (self.handNumbers,
                                                                       str(self.date)[:10],
                                                                       len(self.hits),
                                                                       self.drawResult(self.drawnNumbers, self.hits))
            return retString
        else:
            return 'Brak wynikow!'